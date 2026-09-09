# frozen_string_literal: true
# Load defines helpers only. Invoke run explicitly in SketchUp's main thread.
require 'json'
require 'time'

module CodexSketchupArchitect
  DICT = 'sketchup_architect' unless const_defined?(:DICT)

  def self.runtime_model
    raise 'SketchUp runtime required; system Ruby/stubs cannot model' unless defined?(Sketchup) && Sketchup.respond_to?(:active_model)
    raise 'SketchUp main thread required' unless Thread.current == Thread.main
    model = Sketchup.active_model
    raise 'No active SketchUp model' unless model
    raise 'Exit the current group/component edit context first' unless model.active_path.nil?
    raise 'These helpers require SketchUp 2017+; adapt to older APIs explicitly' if Sketchup.version.to_i < 17
    model
  end

  def self.write_report(path, data)
    temporary = path + '.tmp'
    File.open(temporary, 'w') { |f| f.write(JSON.pretty_generate(data)) }
    File.rename(temporary, path)
  end

  # Call before run, after inspecting the active document. First save names an
  # unnamed model; save_copy preserves the path of an already named model.
  def self.save_checkpoint(path:, expected_guid:)
    raise 'Checkpoint must be outside the helper transaction' if @running
    model = runtime_model
    raise 'Active model changed; inspect again' unless model.guid == expected_guid
    target = File.expand_path(path)
    raise 'Checkpoint must use .skp' unless File.extname(target).downcase == '.skp'
    raise 'Use a fresh checkpoint filename' if File.exist?(target) || File.symlink?(target)
    raise 'Checkpoint directory must exist' unless File.directory?(File.dirname(target))
    previous_path = model.path
    method = previous_path.empty? ? :save : :save_copy
    saved = model.public_send(method, target)
    raise 'Checkpoint save failed; inspect any partial file' unless saved && File.file?(target) && File.size(target) > 0
    expected_path = previous_path.empty? ? target : previous_path
    raise 'Unexpected active path after checkpoint' unless model.path == expected_path
    {path: target, bytes: File.size(target), method: method.to_s,
     previous_model_path: previous_path, model_path: model.path, guid: model.guid}
  end

  # An inventory is evidence, not automatic cleanup or a scene-property backup.
  # Names can repeat; never erase a page solely because its name matches.
  def self.scene_inventory(model)
    {available: true, pages: model.pages.each_with_index.map { |page, i| {index: i, name: page.name} }}
  rescue StandardError => error
    {available: false, error: error.class.name + ': ' + error.message}
  end

  # expected_guid is a freshly inspected snapshot token, not a permanent identity.
  # root_pid=nil creates a new owned root; otherwise updates the specified owned root.
  # The yielded block may modify ONLY that root and explicitly scoped scene/material data.
  def self.run(project_id:, expected_guid:, expected_revision:, report_path:, root_pid: nil)
    raise 'Nested helper transaction rejected' if @running
    model = runtime_model
    raise 'Empty project identity' unless project_id.is_a?(String) && !project_id.empty?
    raise 'Expected revision must be nonnegative integer' unless expected_revision.is_a?(Integer) && expected_revision >= 0
    raise 'Active model changed; inspect again' unless expected_guid.is_a?(String) && model.guid == expected_guid
    root = root_pid && model.find_entity_by_persistent_id(root_pid)
    if root_pid
      raise 'Root must be a top-level group' unless root.is_a?(Sketchup::Group) && model.entities.to_a.include?(root)
      raise 'Target root is locked' if root.locked?
      raise 'Project identity mismatch' unless root.get_attribute(DICT, 'project_id') == project_id
      raise 'Revision mismatch; inspect current state' unless root.get_attribute(DICT, 'revision') == expected_revision
    else
      raise 'New project must start at revision zero' unless expected_revision.zero?
      existing = model.entities.any? { |e| e.get_attribute(DICT, 'project_id') == project_id }
      raise 'Project already exists; inspect its root instead of rerunning creation' if existing
    end
    path = File.expand_path(report_path)
    raise 'Use a fresh report filename' if File.exist?(path) || File.exist?(path + '.tmp')
    raise 'Report directory must exist' unless File.directory?(File.dirname(path))
    record = {schema_version: 1, project_id: project_id, expected_revision: expected_revision,
              model_path: model.path, guid_before: model.guid, status: 'prepared', at: Time.now.utc.iso8601,
              scenes_before: scene_inventory(model)}
    # Persist evidence before any model mutation.
    File.open(path, File::WRONLY | File::CREAT | File::EXCL, 0o600) { |f| f.write(JSON.pretty_generate(record)) }
    @running = true
    opened = false
    committed = false
    begin
      raise 'Could not start operation' unless model.start_operation('SketchUp Architect revision', true)
      opened = true
      if root
        root.make_unique
      else
        root = model.entities.add_group
        root.name = 'Architecture ' + project_id
        root.set_attribute(DICT, 'project_id', project_id)
        root.set_attribute(DICT, 'role', 'project_root')
      end
      yield(model, root)
      raise 'Active model switched during operation' unless Sketchup.active_model == model
      raise 'Build removed its owned root' unless root.valid?
      root.set_attribute(DICT, 'revision', expected_revision + 1)
      raise 'Could not commit operation' unless model.commit_operation
      opened = false
      committed = true
      record.merge!(status: 'committed', revision: expected_revision + 1, root_pid: root.persistent_id)
      record[:scenes_after] = scene_inventory(model)
      write_report(path, record)
      record
    rescue StandardError => error
      state = committed ? 'post_commit_error' : 'not_started'
      if opened
        begin
          state = model.abort_operation ? 'aborted' : 'rollback_failed'
        rescue StandardError => rollback_error
          state = 'rollback_failed'
          record[:rollback_error] = rollback_error.class.name + ': ' + rollback_error.message
        end
      end
      record.merge!(status: state, error: error.class.name + ': ' + error.message,
                    backtrace: (error.backtrace || []).first(10),
                    scenes_after: scene_inventory(model), scene_state_requires_review: true)
      begin
        write_report(path, record)
      rescue StandardError => report_error
        warn 'Report write failed: ' + report_error.message
      end
      raise
    ensure
      @running = false
    end
  end
end
