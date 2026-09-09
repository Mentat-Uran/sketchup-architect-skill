# frozen_string_literal: true
# Read-only model traversal. No actions run on load. Output writes are explicit.
require 'json'
require 'time'

module CodexSketchupArchitect
  DICT = 'sketchup_architect' unless const_defined?(:DICT)

  def self.audit(root: nil, max_entities: 200_000, max_depth: 64)
    raise 'SketchUp runtime required' unless defined?(Sketchup) && Sketchup.respond_to?(:active_model)
    raise 'SketchUp main thread required' unless Thread.current == Thread.main
    model = Sketchup.active_model
    raise 'No active model' unless model
    raise 'Exit edit context before auditing' unless model.active_path.nil?
    raise 'Audit helpers require SketchUp 2017+' if Sketchup.version.to_i < 17
    raise 'Audit limits must be positive integers' unless [max_entities, max_depth].all? { |v| v.is_a?(Integer) && v > 0 }
    if root && !(root.is_a?(Sketchup::Group) && model.entities.to_a.include?(root))
      raise 'Select a top-level project group for this audit'
    end
    report = {schema_version: 1, kind: 'sketchup_architect_audit', complete: true, at: Time.now.utc.iso8601,
              sketchup_version: Sketchup.version, ruby_version: RUBY_VERSION, platform: RUBY_PLATFORM,
              model_path: model.path, model_guid: model.guid,
              project_id: root && root.get_attribute(DICT, 'project_id'),
              revision: root && root.get_attribute(DICT, 'revision'),
              capabilities: {entities_builder: model.entities.respond_to?(:build), save_copy: model.respond_to?(:save_copy)},
              counts: Hash.new(0), elements: [], errors: [], warnings: [],
              quantities: {gfa_m2_by_level: Hash.new(0.0), net_m2_by_space: Hash.new(0.0)}}
    visited = 0
    failures = Hash.new(0)
    notes = Hash.new(0)
    walk = nil
    walk = lambda do |entities, transform, path, definitions, depth|
      if depth > max_depth
        report[:complete] = false
        failures['Maximum nesting depth exceeded'] += 1
        return
      end
      ids_here = {}
      entities.each do |entity|
        visited += 1
        if visited > max_entities
          report[:complete] = false
          failures['Entity limit exceeded; audit is truncated'] += 1
          break
        end
        unless entity.valid?
          failures['Invalid entity'] += 1
          next
        end
        report[:counts][entity.typename] += 1
        pid = entity.persistent_id
        instance_path = path + [pid]
        semantic = entity.get_attribute(DICT, 'semantic_id')
        if semantic
          failures['Duplicate semantic ID in one entities context: ' + semantic.to_s] += 1 if ids_here[semantic]
          ids_here[semantic] = true
        end
        if entity.is_a?(Sketchup::Face) || entity.is_a?(Sketchup::Edge)
          failures['Raw geometry assigned to a tag other than Untagged'] += 1 unless entity.layer == model.layers[0]
        end
        if entity.is_a?(Sketchup::Face)
          failures['Zero-area face'] += 1 if entity.area <= 0
          kind = entity.get_attribute(DICT, 'quantity_kind')
          if kind
            vertices = entity.vertices.map { |v| v.position.transform(transform) }
            spread = vertices.map(&:z).minmax
            if spread[1] - spread[0] > 0.001 / 0.0254
              failures['Quantity face is not horizontal'] += 1
            end
            field, key = if kind == 'gfa'
                           [:gfa_m2_by_level, entity.get_attribute(DICT, 'level_id')]
                         elsif kind == 'net'
                           [:net_m2_by_space, entity.get_attribute(DICT, 'space_id')]
                         end
            if field && key.is_a?(String) && !key.empty?
              report[:quantities][field][key] += entity.area(transform) * (0.0254**2)
            else
              failures['Quantity face has invalid kind or missing level/space ID'] += 1
            end
          end
        elsif entity.is_a?(Sketchup::Edge)
          notes['Loose edges (may include intentional reference lines)'] += 1 if entity.faces.empty?
          notes['Edges with more than two faces'] += 1 if entity.faces.length > 2
        elsif entity.is_a?(Sketchup::Group) || entity.is_a?(Sketchup::ComponentInstance)
          definition = entity.definition
          combined = transform * entity.transformation
          determinant = combined.xaxis.cross(combined.yaxis).dot(combined.zaxis)
          failures['Singular transformation'] += 1 if determinant.abs < 1.0e-12
          notes['Mirrored instance; inspect front/back materials and normals'] += 1 if determinant < 0
          expected = entity.get_attribute(DICT, 'expected_solid') == true
          solid = entity.respond_to?(:manifold?) ? entity.manifold? : nil
          failures['Expected solid is not manifold'] += 1 if expected && solid != true
          notes['Unnamed group/component'] += 1 if entity.name.empty?
          report[:elements] << {path: instance_path, semantic_id: semantic, name: entity.name,
                               role: entity.get_attribute(DICT, 'role'), locked: entity.locked?,
                               definition_instances: definition.instances.length, manifold: solid,
                               expected_solid: expected, transformation: combined.to_a}
          if definitions.include?(definition)
            report[:complete] = false
            failures['Recursive definition detected'] += 1
          else
            walk.call(definition.entities, combined, instance_path, definitions + [definition], depth + 1)
          end
        end
        break unless report[:complete]
      end
    end
    walk.call(root ? [root] : model.entities, Geom::Transformation.new, [], [], 0)
    report[:errors] = failures.map { |message, count| "#{message} (#{count})" }
    report[:warnings] = notes.map { |message, count| "#{message} (#{count})" }
    report[:warnings] << 'Visual/architectural QA required: this audit does not prove face orientation, clashes, physical access, site fit or regulatory compliance.'
    report
  end

  def self.save_audit(path, **options)
    expanded = File.expand_path(path)
    report = audit(**options)
    File.open(expanded, File::WRONLY | File::CREAT | File::EXCL, 0o600) { |f| f.write(JSON.pretty_generate(report)) }
    report
  end
end
