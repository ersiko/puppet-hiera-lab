class facts() {
  file { '/etc/facts':
    content => template('facts/factlist.erb')
  }
}
