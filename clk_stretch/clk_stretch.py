import os
import sys
import subprocess
import traceback
import platform

def build(set_exec_name, get_exec_name):
    print("Building i2c1 clock stretch timeout setter and getter")
    subprocess.check_output(["gcc", "-o", set_exec_name, "i2c1_set_clkt_tout.c"])
    subprocess.check_output(["gcc", "-o", get_exec_name, "i2c1_get_clkt_tout.c"])

def copy(set_exec_name, get_exec_name, dest_path):
    print("Copying i2c1 clock stretch timeout setter and getter to " + dest_path)
    subprocess.check_output(["mv", set_exec_name, dest_path])
    subprocess.check_output(["mv", get_exec_name, dest_path])

def set_clk_stretch_timeout(set_exec_name, get_exec_name, clkt_tout):
    print("Setting i2c1 clock stretch timeout value to " + str(clkt_tout))
    subprocess.check_output([set_exec_name, str(clkt_tout)])
    print("Checking i2c1 clock stretch timeout value")
    output = subprocess.check_output([get_exec_name])
    if type(output) != str:
        output = output.decode("utf-8")
    if str(clkt_tout) not in output:
        raise Exception("Failed to set clock stretch timeout value! " + output)

def update_rc_local(dest_path, set_exec_name, clkt_tout):
    exit_token = "exit 0"
    clks_line = dest_path + set_exec_name + " " + str(clkt_tout)
    updated = False
    with open("/etc/rc.local", "r+") as f:
        lines = f.readlines()
        for i in range(0, len(lines)):
            if set_exec_name in lines[i]:
                print("rc.local already updated")
                updated = True
                break
            if lines[i].startswith(exit_token):
                lines[i] = lines[i].replace(exit_token, clks_line + "\n\n" + exit_token + "\n")
                # return pointer to top of file so we can re-write the content with replaced string
                f.seek(0)
                # clear file content
                f.truncate()
                # re-write the content with the updated content
                f.write("".join(lines))
                print("rc.local updated")
                updated = True
                break
    if not updated:
        raise Exception("Failed to update rc.local!")

def setup_clk_stretch_timeout(clk_stretch_timeout, baudrate):
    dest_path = "/usr/local/bin/"
    set_exec_name = "i2c1_set_clkt_tout"
    get_exec_name = "i2c1_get_clkt_tout"
    clkt_tout = int(float(clk_stretch_timeout) * float(baudrate))

    build(set_exec_name, get_exec_name)
    copy(set_exec_name, get_exec_name, dest_path)
    set_clk_stretch_timeout(set_exec_name, get_exec_name, clkt_tout)
    update_rc_local(dest_path, set_exec_name, clkt_tout)

def main():
    RASPBERRY_PI = 'raspberry-pi'
    PLATFORM = 'Unknown'
    if platform.system().lower() == 'linux':
        if platform.linux_distribution()[0].lower() == 'debian':
            try:
                with open('/proc/cpuinfo') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('Hardware') and ('BCM2708' in line or 'BCM2709' in line):
                            PLATFORM = RASPBERRY_PI
                            setup_clk_stretch_timeout(clk_stretch_timeout=0.2, baudrate=100000)
                            break
            except:
                traceback.print_exc()

    LEGAL_PLATFORMS = RASPBERRY_PI
    assert PLATFORM in LEGAL_PLATFORMS, "Don't understand platform"

if __name__ == '__main__':
  main()
