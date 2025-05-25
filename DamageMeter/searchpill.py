#모비노기 패킷 분석 코드 v25.05.25



from scapy.all import sniff, IP, Raw, get_if_addr, conf
import re
from textwrap import wrap
import struct
import zlib

my_ip = get_if_addr(conf.iface)

PORT = 16000

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
    # 3a 04 00 00 00 00 00 00 00 ?? ?? 00 00 ?? 00 00 00
    start_matches = (
        data[0:2] == b'\x3A\x04' and
        data[2:9] == b'\x00\x00\x00\x00\x00\x00\x00' and
        data[11:13] == b'\x00\x00' and
        data[14:17] == b'\x00\x00\x00'
    )
    end_pattern = b'\xAC\x04\x00\x00\x00\x00\x00\x00\x00'
    end_matches = data.endswith(end_pattern)
    return start_matches and end_matches

def tryprint(raw_data):
    # 패킷 출력 방식
    printtohex = True
    printtostr = True
    printtoint = False

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

    # [2] = 2708224 이동 시작
    # [2] = 2712064 이동
    # [2] = 2708736 이동 종료
    # [2] = 306944 평타
    # [2] = 334336 지역챗
    # [2] = 2674176 
    
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

    if printtoint: print(printint)

    utf16list = utf16leprint(raw_data)
    if len(utf16list[0]) != 0 and printtostr:
        print((utf16list[0])) # str 데이터 출력
        ''
    
    if printtohex: print(raw_data.hex(" "))
    

def packet_callback(packet):
    if Raw in packet:
        #print(packet.summary())
        tryprint(packet[Raw].load)
                

print(f"STarting tcp port : {PORT}...")
sniff(filter=f"tcp port {PORT} and dst host {my_ip}", prn=packet_callback, store=0)
#sniff(filter=f"tcp port {PORT}", prn=packet_callback, store=0)
