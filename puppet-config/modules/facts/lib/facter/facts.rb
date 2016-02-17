Facter.add("env") do
  setcode do
    Facter.value('fqdn').split('.')[-3]
  end
end

Facter.add("datacenter") do
  setcode do
    Facter.value('fqdn').split('.')[-4]
  end
end
