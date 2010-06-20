
Given /페이지의 캐쉬가 존재/ do
  #puts "why not?"
end
Given /페이지의 캐쉬가 안 존재/ do
  #puts "why not?"
end

When /로컬로 (.*) 노트의 (.*) 페이지를 (.*) 형식으로 읽/ do |note,page_id,format|
  #puts [note, page_id, format].inspect
end
When /원격으로 (.*) 노트의 (.*) 페이지를 (.*) 형식으로 읽/ do |note,page_id,format|
  #puts [note, page_id, format].inspect
end

Then /경로 (.*)\s*를 읽/ do |path|
  #puts path
end
Then /경로 (.*)\s*에 내용을 저장하/ do |path|
  #puts path
end

Then /springnote.com 에서 페이지의 내용을 읽/ do
end

Then /내용을 보여준/ do
end
