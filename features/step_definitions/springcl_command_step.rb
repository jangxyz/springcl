def run_python(cmd)
  cmd = cmd.strip.gsub(/'/) {|quote| '\\' + quote}
  puts `python -c '#{cmd}'`
  raise "error running python" unless $?.exitstatus.zero?
end
  

When /로컬에서 springcl (.*)을 하면/ do |cmd|
  run_python <<-CMD
	import springcl; springcl.#{cmd}("--local-only")
  CMD
end

