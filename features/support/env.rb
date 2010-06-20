# local cache mode!
Before do 
  # temp testbed @test_dir
  @test_dir = "~/tmp/springcl_test/home/" + Time.now.to_i.to_s
  @test_dir = File.expand_path(@test_dir)
  @already_existing = {}
  @test_dir[1..-1].split('/').inject('') do |path, dir|
    path += '/' + dir
    @already_existing[path] = File.exists? path
    path
  end

  # create directories
  @already_existing.keys.sort.each do |dir|
    Dir.mkdir dir unless @already_existing[dir]
  end
end

After do
  # remove @test_dir
  @already_existing.keys.sort.reverse.each do |dir|
    Dir.rmdir dir unless @already_existing[dir]
  end
end

