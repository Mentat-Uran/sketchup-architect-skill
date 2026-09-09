# frozen_string_literal: true
# Explicit offline test doubles; never connects to SketchUp or a native API.
require 'tmpdir'
require 'json'
require_relative 'model_session'
require_relative 'model_audit'

raise 'Tests must run in system Ruby, outside SketchUp' if defined?(Sketchup)
checks = []
verify = lambda do |name, &block|
  raise 'FAIL: ' + name unless block.call
  checks << name
end
begin
  CodexSketchupArchitect.runtime_model
  raise 'Runtime guard did not reject system Ruby'
rescue RuntimeError => e
  verify.call('plain Ruby cannot model') { e.message.include?('runtime required') }
end

module Geom
  class Vector3d
    attr_reader :x, :y, :z
    def initialize(x, y, z); @x, @y, @z = x, y, z; end
    def cross(v); self.class.new(y*v.z-z*v.y, z*v.x-x*v.z, x*v.y-y*v.x); end
    def dot(v); x*v.x+y*v.y+z*v.z; end
  end
  class Transformation
    attr_reader :sx, :sy, :sz
    def initialize(sx=1.0, sy=1.0, sz=1.0); @sx, @sy, @sz = sx, sy, sz; end
    def *(other); self.class.new(sx*other.sx, sy*other.sy, sz*other.sz); end
    def xaxis; Vector3d.new(sx,0,0); end
    def yaxis; Vector3d.new(0,sy,0); end
    def zaxis; Vector3d.new(0,0,sz); end
    def to_a; [sx,sy,sz]; end
  end
  class Point3d
    attr_reader :z
    def initialize(z=0); @z=z; end
    def transform(t); self.class.new(z*t.sz); end
  end
end

module Sketchup
  Definition = Struct.new(:entities, :instances)
  Vertex = Struct.new(:position)
  class Entity
    attr_accessor :name, :layer
    attr_reader :persistent_id
    def initialize(pid); @persistent_id=pid; @attributes={}; @name='Object'; @layer=0; end
    def get_attribute(dict,key); @attributes[[dict,key]]; end
    def set_attribute(dict,key,value); @attributes[[dict,key]]=value; end
    def valid?; true; end
    def typename; self.class.name.split('::').last; end
    def locked?; false; end
  end
  class Face < Entity
    def area(transform=nil); 100.0 * (transform ? (transform.sx*transform.sy).abs : 1.0); end
    def vertices; Array.new(4) { Vertex.new(Geom::Point3d.new) }; end
  end
  class Edge < Entity
    def faces; []; end
  end
  class Entities < Array
    def add_group; group=Group.new(length+100); self << group; group; end
  end
  class Group < Entity
    attr_accessor :transformation, :is_solid
    attr_reader :entities, :definition
    def initialize(pid)
      super(pid); @entities=Entities.new; @transformation=Geom::Transformation.new
      @definition=Definition.new(@entities,[self]); @is_solid=true
    end
    def make_unique; self; end
    def manifold?; @is_solid; end
  end
  class ComponentInstance < Group; end
  class Model
    attr_accessor :active_path, :entities, :fail_commit, :path, :save_behavior
    attr_reader :events, :pages
    def initialize; @entities=Entities.new; @events=[]; @pages=[]; @path='/offline/double.skp'; end
    def guid; 'observed-guid'; end
    def save(target)
      @events << 'save'
      return false if save_behavior == :false
      File.write(target, save_behavior == :empty ? '' : 'offline snapshot')
      @path=target
      true
    end
    def save_copy(target)
      raise 'Model must be saved before copying' if path.empty?
      previous=path
      result=save(target)
      @events[-1]='save_copy'
      @path=previous
      result
    end
    def layers; [0]; end
    def start_operation(*args); @snapshot=Marshal.dump(@entities); @events << 'start'; true; end
    def commit_operation; return false if fail_commit; @events << 'commit'; true; end
    def abort_operation; @entities=Marshal.load(@snapshot); @events << 'abort'; true; end
    def find_entity_by_persistent_id(pid); @entities.find { |e| e.persistent_id == pid }; end
  end
  def self.active_model; @model ||= Model.new; end
  def self.version; '25.0.659'; end
end

Dir.mktmpdir('architect-contract-') do |dir|
  model=Sketchup.active_model
  model.path=''
  first=File.join(dir,'first.skp')
  cp=CodexSketchupArchitect.save_checkpoint(path:first,expected_guid:model.guid)
  verify.call('unnamed checkpoint uses first save and records new path') { cp[:method]=='save' && model.path==first && File.size(first)>0 }
  second=File.join(dir,'second.skp')
  cp=CodexSketchupArchitect.save_checkpoint(path:second,expected_guid:model.guid)
  verify.call('named checkpoint uses save_copy and preserves active path') { cp[:method]=='save_copy' && model.path==first && File.read(second)==File.read(first) }
  count=model.events.length
  begin
    CodexSketchupArchitect.save_checkpoint(path:first,expected_guid:model.guid)
    raise 'overwrite accepted'
  rescue RuntimeError => e
    verify.call('checkpoint refuses existing file before save') { e.message.include?('fresh checkpoint') && model.events.length==count }
  end
  [:false,:empty].each do |behavior|
    model.save_behavior=behavior
    begin
      CodexSketchupArchitect.save_checkpoint(path:File.join(dir,"failed-#{behavior}.skp"),expected_guid:model.guid)
      raise 'bad save accepted'
    rescue RuntimeError => e
      verify.call("checkpoint rejects #{behavior} save result") { e.message.include?('Checkpoint save failed') }
    end
  end
  model.save_behavior=nil
  begin
    CodexSketchupArchitect.save_checkpoint(path:File.join(dir,'wrong.skp'),expected_guid:'other')
    raise 'wrong document accepted'
  rescue RuntimeError => e
    verify.call('checkpoint rejects wrong document') { e.message.include?('Active model changed') }
  end
  args={project_id:'offline-project', expected_guid:model.guid, expected_revision:0, report_path:File.join(dir,'new.json')}
  result=CodexSketchupArchitect.run(**args) { |_m, root| root.name='Concept' }
  verify.call('creation commits revision and owned root') { result[:status]=='committed' && result[:revision]==1 && model.entities.length==1 }
  root=model.entities.first
  root_pid=root.persistent_id
  begin
    CodexSketchupArchitect.run(**args.merge(report_path:File.join(dir,'duplicate.json'))) { raise 'must not run' }
  rescue RuntimeError => e
    verify.call('duplicate creation rejected before mutation') { e.message.include?('already exists') && model.entities.length==1 }
  end
  begin
    CodexSketchupArchitect.run(**args.merge(root_pid:root_pid,expected_revision:99,report_path:File.join(dir,'wrong.json'))) {}
  rescue RuntimeError => e
    verify.call('stale revision rejected') { e.message.include?('Revision mismatch') }
  end
  begin
    CodexSketchupArchitect.run(**args.merge(root_pid:root_pid,expected_revision:1,expected_guid:'other',report_path:File.join(dir,'guid.json'))) {}
  rescue RuntimeError => e
    verify.call('wrong document rejected') { e.message.include?('Active model changed') }
  end
  inside=File.join(dir,'inside-operation.skp')
  begin
    CodexSketchupArchitect.run(**args.merge(root_pid:root_pid,expected_revision:1,report_path:File.join(dir,'nested-save.json'))) do
      CodexSketchupArchitect.save_checkpoint(path:inside,expected_guid:model.guid)
    end
    raise 'transaction checkpoint accepted'
  rescue RuntimeError => e
    verify.call('checkpoint inside transaction rejected without writing') { e.message.include?('outside the helper transaction') && !File.exist?(inside) }
  end
  failure_path=File.join(dir,'failed.json')
  begin
    CodexSketchupArchitect.run(**args.merge(root_pid:root_pid,expected_revision:1,report_path:failure_path)) do |_m, current|
      model.pages << Struct.new(:name).new('Page surviving geometry abort')
      current.name='Broken'; raise 'deliberate geometry failure'
    end
  rescue RuntimeError
    verify.call('exception aborts and records failure') { model.entities.first.name=='Concept' && JSON.parse(File.read(failure_path))['status']=='aborted' }
    failure=JSON.parse(File.read(failure_path))
    verify.call('scene surviving abort is reported without destructive cleanup') do
      failure['scenes_before']['pages'].empty? && failure['scenes_after']['pages'].length==1 &&
        failure['scene_state_requires_review'] && model.pages.length==1
    end
  end
  model.active_path=[model.entities.first]
  begin
    CodexSketchupArchitect.runtime_model
  rescue RuntimeError => e
    verify.call('active edit context rejected') { e.message.include?('edit context') }
  end
  model.active_path=nil
  root=model.entities.first
  assembly=Sketchup::Group.new(500)
  face=Sketchup::Face.new(501)
  face.set_attribute(CodexSketchupArchitect::DICT,'quantity_kind','gfa')
  face.set_attribute(CodexSketchupArchitect::DICT,'level_id','L0')
  assembly.entities << face
  assembly.transformation=Geom::Transformation.new(2,3,1)
  root.entities << assembly
  repeated=Sketchup::ComponentInstance.new(502)
  repeated.instance_variable_set(:@definition, assembly.definition)
  root.entities << repeated
  report=CodexSketchupArchitect.audit(root:root)
  expected=700.0*(0.0254**2)
  verify.call('nested transforms and repeated instances count actual face areas') { (report[:quantities][:gfa_m2_by_level]['L0']-expected).abs<1e-10 }
  face.layer=9
  report=CodexSketchupArchitect.audit(root:root)
  verify.call('raw tag error detected') { report[:errors].any? { |e| e.include?('Raw geometry') } }
  assembly.set_attribute(CodexSketchupArchitect::DICT,'expected_solid',true)
  assembly.is_solid=false
  verify.call('expected non-solid detected') { CodexSketchupArchitect.audit(root:root)[:errors].any? { |e| e.include?('not manifold') } }
  verify.call('truncated audit is incomplete') { !CodexSketchupArchitect.audit(root:root,max_entities:1)[:complete] }
  verify.call('audit preserves model entity count and name') { model.entities.length==1 && root.name=='Concept' }
end
puts JSON.pretty_generate({ok:true, mode:'offline_test_doubles_no_native_geometry', checks:checks})
