[ci_servers]
${ci_ip} ansible_user=${ssh_user} ansible_ssh_private_key_file=${ssh_key}

[target_servers]
${target_ip} ansible_user=${ssh_user} ansible_ssh_private_key_file=${ssh_key}
