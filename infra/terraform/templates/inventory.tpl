[ci_servers]
${ci_ip} ansible_user=${ssh_user} ansible_ssh_private_key_file=${ssh_key} ansible_ssh_common_args='-o StrictHostKeyChecking=no'

[target_servers]
${target_ip} ansible_user=${ssh_user} ansible_ssh_private_key_file=${ssh_key} ansible_ssh_common_args='-o StrictHostKeyChecking=no'