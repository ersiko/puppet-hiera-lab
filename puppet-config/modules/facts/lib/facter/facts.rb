Facter.add("env") do
  setcode do
    Facter.value('fqdn').split('.')[-3]
  end
end
