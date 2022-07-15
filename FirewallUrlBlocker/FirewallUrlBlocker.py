import subprocess
import socket
import sys
import ctypes, os
import types
import traceback

def is_admin():
	try:
		is_admin = os.getuid() == 0
	except AttributeError:
		is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0

	return is_admin

def get_ip_by_url(url):
	try:
		ip = socket.gethostbyname(url)
		return ip
	except Exception as ex:
		print(f"Failed to get ip for {url}: {ex}")
	return None

def shell_firewall_add_rule(rule_name, direction="out", action="block", protocol="tcp", localIp="any", remoteIp="any"):
	return ["netsh", "advfirewall", "firewall", "add", "rule", f"name=\"{rule_name}\"", 
		 f"dir={direction}", f"action={action}", f"protocol={protocol}", f"localip={localIp}", f"remoteip={remoteIp}"]

def shell_firewall_show_rule(rule_name):
	return ["netsh", "advfirewall", "firewall", "show", "rule", f"name={rule_name}"]

def shell_list_to_string(shell_list):
	text = ""
	for shell_segment in shell_list:
		text += shell_segment + " "

	return text

def block_url(url):
	rule_name = f"FirewallUrlBlocker_{url}_block"

	shell_show_rule = shell_firewall_show_rule(rule_name)
	print(f"Invoking shell with command {shell_list_to_string(shell_show_rule)}...")

	with subprocess.Popen(shell_show_rule, stdout=subprocess.PIPE, universal_newlines=True) as cmd_process:
		
		exit_code = cmd_process.wait()
		
		if exit_code == 0:
			print(f"Rule {rule_name} already exists! This rule will not be overwritten")
			return False	

	print(f"Blocking url {url}...")
	ip = get_ip_by_url(url);

	if ip is None:
		print("Rule will not be created, because DNS lookup failed")
		return False

	print(f"DNS lookup result: {ip}")	

	shell = shell_firewall_add_rule(rule_name, remoteIp=ip)

	print(f"Invoking shell with command {shell_list_to_string(shell)}...")

	with subprocess.Popen(shell, stdout=subprocess.PIPE, universal_newlines=True) as cmd_process:
		
		exit_code = cmd_process.wait()
		
		if exit_code == 0:
			print("Rule created!")
			return True
		else:
			print("Failed to create a rule!")
			return False


if not is_admin():
	print("Run as admin! Rules will not be created.")
	exit(-1)

url_list_file_path = sys.argv[1]

if url_list_file_path is None:
	print("Usage: python FirewallUrlBlocker.py path_to_url_list")
	exit(-1)

print(f"Reading {url_list_file_path}...")

total_counter = 0
success_counter = 0

with open(url_list_file_path) as url_list_file:
	for line in url_list_file:
		if block_url(line.strip()):
			success_counter += 1
		total_counter += 1
		print()

print(f"Done {success_counter}/{total_counter}!")

exit(0)