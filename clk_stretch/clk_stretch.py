from subprocess import call
import platform

def rpi_clk_stretch_timeout(clk_stretch_timeout, baudrate):
    dest_path = '/usr/local/bin/'
    set_exec_name = 'i2c1_set_clkt_tout'
    get_exec_name = 'i2c1_get_clkt_tout'
    clkt_tout = int(float(clk_stretch_timeout) * float(baudrate))
    line_to_add = dest_path + set_exec_name + " " + str(clkt_tout)
    
    print("Building i2c1 clock stretch setter and getter.")
    call(["gcc","-o", set_exec_name, "i2c1_set_clkt_tout.c"])
    call(["gcc","-o", get_exec_name, "i2c1_get_clkt_tout.c"])
    
    print("Copying i2c1 clock stretch setter and getter to " + dest_path + ".")
    call(["mv",set_exec_name, dest_path])
    call(["mv",get_exec_name, dest_path])
    
    print("Setting i2c1 clock stretch value.")
    call([set_exec_name, clkt_tout])
    
    print("Checking i2c1 clock stretch value.")
    call([get_exec_name])
    
    print("Udating rc.local.")
    # open file with r+b (allow write and binary mode)
    f = open('/etc/rc.local', 'r+b')   
    # read entire content of file into memory
    f_lines = f.readlines()
    
    exit_token = 'exit 0'
    rc_local_updated = False
    for i in range(0, len(f_lines)):
        if set_exec_name in f_lines[i]:
            f_lines[i] = line_to_add + "\n"
            rc_local_updated = True
            break
        if exit_token in f_lines[i]:
            f_lines[i] = line_to_add + "\n\n" + exit_token + "\n"
            rc_local_updated = True
            break
        
    if not rc_local_updated:
        print ("Failed to update rc.local!!!")
    
    # return pointer to top of file so we can re-write the content with replaced string
    f.seek(0)
    # clear file content 
    f.truncate()
    # re-write the content with the updated content
    f.write("".join(f_lines))
    # close file
    f.close()

def main():
    RASPBERRY_PI = 'raspberry-pi'
    
    PLATFORM = 'Unknown'
    SYSTEM = platform.system().lower()
    if SYSTEM == 'linux':
        if platform.linux_distribution()[0].lower() == 'debian':
            try:
                with open('/proc/cpuinfo') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('Hardware') and ('BCM2708' in line or 'BCM2709' in line):
                            PLATFORM = RASPBERRY_PI
                            rpi_clk_stretch_timeout(clk_stretch_timeout=0.2, baudrate=100000)
                            break
            except:
                pass
    
    LEGAL_PLATFORMS = RASPBERRY_PI
    assert PLATFORM in LEGAL_PLATFORMS, "Don't understand platform"

if __name__ == '__main__':
  main()
