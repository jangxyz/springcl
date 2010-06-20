def eval_dirvar(dirvar)
  dirvar.split('/').reduce('') do |path, dirvar|
    dir = case dirvar
      when /^@.*/            then instance_variable_get(dirvar)
      when /^\$(.*)/         then ENV[$1]
      when /^('.*')|(".*")$/ then dirvar[1...-1]
      else                        dirvar
    end
    path += '/' + dir.to_s
  end[1..-1]
end

def dir_exists?(dirvar)
  File.exists? eval_dirvar(dirvar)
end


Given /(.*) 디렉토리가 안 존재[하한]/ do |dirvar|
  raise "#{eval_dirvar dirvar}은 존재하지 않습니다." if dir_exists? dirvar
end
Then /(.*) 디렉토리가 존재[하한]/ do |dirvar|
  raise "#{eval_dirvar dirvar}은 존재하지 않습니다." unless dir_exists? dirvar
end

Then /(.*) 디렉토리는 비어있/ do |dirvar|
  dirname = instance_variable_get(dirvar)
  files    = Dir.new(dirname).entries.reject {|name| %w(. ..).member? name}
  raise "#{dirname}은 비어있지 않습니다." unless files.empty?
end

Then /다음 디렉토리들이 생성되어야 한다/ do |directories_table|
  puts directories_table.hashes.map(&:values).flatten.inspect
end


