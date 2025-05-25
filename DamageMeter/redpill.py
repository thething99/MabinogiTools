#모비노기 데미지 프린터 v25.05.25
#미완성 코드입니다!!!!



from scapy.all import sniff, IP, Raw, get_if_addr, conf
import re
from textwrap import wrap
import struct
import zlib

my_ip = get_if_addr(conf.iface)

PORT = 16000

skilllist = [ # 인식 가능한 스킬 리스트, 직업별로 추가 필요
    'RangeDefaultAttack_1',
    'RangeDefaultAttack_2',
    'RangeDefaultAttack_3',
    'MeleeDefaultAttack_1',
    'MeleeDefaultAttack_2',
    'FireMage_FireStorm',
    'RapidFire_Tier1A',
    'RapidFire_Tier2A',
    'Flashover_HitPª',
    'Idle',
    'Elemental_Common_Hit_Bleed',
    'GreatSwordWarrior_Slash_Back',
    'Arbalist_MountingShock',
    'Arbalist_GustingBolt_01',
    'Arbalist_GustingBolt_02',
]

blacklist = [
    '_Backdraft_Trail_',
    'FireStorm_Tie',
    'Script',
    'SkillAI',
    'LoopAI',
    '_Buff_End',
]

def toutf16le(text):
    return text.encode('utf-16le')

def utf16leprint(hex_bytes, min_chars: int = 4):
    results = []
    rsoffset = 0
    rsdone = False
    i = 0
    while i < len(hex_bytes) - min_chars * 2:
        try:
            chunk = hex_bytes[i:i + min_chars * 2]
            decoded = chunk.decode('utf-16le')

            if not re.fullmatch(r"[a-zA-Z0-9가-힣 _\-\.\:/()\[\]]+", decoded):
                i += 2
                continue

            for j in range(i + min_chars * 2, len(hex_bytes), 2):
                try:
                    extended = hex_bytes[i:j].decode('utf-16le')
                    if not re.fullmatch(r"[a-zA-Z0-9가-힣 _\-\.\:/()\[\]]+", extended):
                        break
                    if not rsdone: rsoffset = j
                    decoded = extended
                except:
                    print('err')
                    break
            rsdone = True
            results.append(decoded)
            i = j 
        except:
            i += 2

    return [results,rsoffset]

def bytetoint(hex_bytes, offset = 0):
    if len(hex_bytes) + 4 < offset:
        return 0
    chunk = hex_bytes[offset:offset+4]
    #print(chunk.hex(" "))
    if len(chunk) == 4:
        int_val = struct.unpack('<I', chunk)[0]
        return int_val
    
def matchdata(data):
    start_matches = (
        data[0:2] == b'\x3A\x04' and
        data[2:9] == b'\x00\x00\x00\x00\x00\x00\x00' and
        data[11:13] == b'\x00\x00' and
        data[14:17] == b'\x00\x00\x00'
    )
    end_pattern = b'\xAC\x04\x00\x00\x00\x00\x00\x00\x00'
    end_matches = data.endswith(end_pattern)
    return start_matches and end_matches

def getburn(data: bytes):
    # 00 00 00 00 00 01 04 00 00 00 03 05 00 00 43 00 00 00 00 + 20
    pattern = b'\x00\x00\x00\x00\x00\x01\x04\x00\x00\x00\x03\x05\x00\x00\x43\x00\x00\x00\x00'
    damages = []
    for match in re.finditer(pattern, data, flags=re.DOTALL):
        start = match.end() + 20
        if len(data) >= start + 4:
            vbytes = data[start:start+4]
            value = int.from_bytes(vbytes, byteorder='little')
            damages.append(value)
    if len(damages) > 0: return damages
    return [0]

def getdamage(data: bytes, pattern):
    damages = []
    for match in re.finditer(pattern, data, flags=re.DOTALL):
        start = match.end() 
        if len(data) >= start + 4:
            value_bytes = data[start:start+4]
            value = int.from_bytes(value_bytes, byteorder='little')
            damages.append(value)
    if len(damages) > 0: return damages
    return [0]

def tryprint(raw_data):
    detec = False
    filterdata2 = [
        2708736,
        2708224,
        2572544,
        334336,
        2605568,
        2624768,
        2621440,   
        2625024,
        2674176,
        2712064,
    ]
    
    printint = ''
    valsint = []
    
    if len(raw_data) < 32: return # 길이 필터링
    if not matchdata(raw_data): return # 헤더 필터링
    for x in blacklist:
        if toutf16le(x) in raw_data: return # str 필터링
        ''
    # int 변환, hex보다 비교가 쪼끔 쉬움
    for i in range(0, len(raw_data), 4):
        chunk = raw_data[i:i+4]
        if len(chunk) == 4:
            int_val = struct.unpack('<I', chunk)[0]
            printint += f"{int_val} "
            valsint.append(int_val)
        
    if valsint[2] in filterdata2: return #int 필터링


    burndamage = getburn(raw_data) # 지속 데미지 출력
    for x in burndamage:
        if x != 0:
            print('burn : ' + str(x))

    for x in skilllist: # 공격 데미지 출력
        if toutf16le(x) in raw_data: 
            detec = True
            damages = getdamage(raw_data, toutf16le(x))
            for y in damages:
                print(x + " : " + str(y))
    return
    
    

def packet_callback(packet):
    if Raw in packet:
        tryprint(packet[Raw].load)
                

print(f"STarting tcp port : {PORT}...")
sniff(filter=f"tcp port {PORT} and dst host {my_ip}", prn=packet_callback, store=0)
#sniff(filter=f"tcp port {PORT}", prn=packet_callback, store=0)
