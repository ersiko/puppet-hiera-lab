Facter.add('role') do
  setcode do
    hostname = Facter.value('hostname')
    match = hostname.match /^(\D+)/
    role = match.captures[0]
    role
  end
end

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
