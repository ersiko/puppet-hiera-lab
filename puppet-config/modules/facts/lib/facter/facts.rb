Facter.add("client") do
  setcode do
    Facter.value('fqdn').split('.')[-2]
  end
end

Facter.add('role') do
  setcode do
    clientid = Facter.value("client")  
    case clientid
    when "client1"
      hostname = Facter.value('hostname')
      match = hostname.match /^(\D+)/
      role = match.captures[0]
      role
    when "client2"
      hostname = Facter.value('fqdn').split('.')[0][1..-1]    
      match = hostname.match /^(\D+)/        
      role = match.captures[0]
      if role == 'web'
        'webserver'
      elsif role == 'db'
        'mysql'
      end                 
    end
  end  
end  
   
Facter.add("datacenter") do
  setcode do
    Facter.value('fqdn').split('.')[-4]
  end
end  
   
Facter.add("env") do
  setcode do
    clientid = Facter.value("client")
    case clientid
    when "client1"
      Facter.value('fqdn').split('.')[-3]
    when "client2"
      if Facter.value('fqdn').split('')[0] == 'p'
        'prod'
      elsif Facter.value('fqdn').split('')[0] == 'd'
        'dev'
      elsif Facter.value('fqdn').split('')[0] == 's'
        'stage'
      end                                     
    end
  end  
end  
