class webpage($connection_string) {
  file { '/var/www/html/index.html':
    content => template('webpage/index.html.erb')
  }
}
