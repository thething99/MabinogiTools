#모비노기 패킷 분석 코드 v25.05.26
# S - 캡처 중지
# R - 캡처 시작
# E - 데이터 초기화
# RE - 캡처 시작 및 데이터 초기화
# 숫자 - 캡처된 패킷 내에서 데미지 검색
# Q - 종료

# 코드 실행 - 스킬 사용 - S 입력 - 데미지 입력 - 패킷 결과 확인 - RE 입력 - 다른 스킬 사용 - 반복


from scapy.all import sniff, IP, Raw, get_if_addr, conf
import re
from textwrap import wrap
import struct
import threading
import queue
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
import os

my_ip = get_if_addr(conf.iface)

PORT = 16000

capture = True
capture_lock = threading.Lock()
packetprocess = queue.Queue()

packets = []
                    

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

def utf16leprint(hex_bytes, min_chars: int = 2):
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
    
def findinbytes(val):
    global packets
    reslt = 0
    for packet in packets:
        if val in packet:
            reslt += 1
            print(packet.hex(" "))
            idx = packet.find(val)
            padding = b'\x00\x00\x00'
            search_start = max(0, idx - 100)  
            pre_data = packet[search_start:idx]
            padding_idx = pre_data.rfind(padding)
            if padding_idx == -1:
                continue
            stringbytes = pre_data[padding_idx + len(padding):]
            stringdata = ''
            try:
                stringdata = stringbytes.decode('utf-16le')
            except UnicodeDecodeError:
                stringdata = ''
            print(stringdata)
    print(str(reslt)+' found / '+val.hex(" ") + ' / in packets ' + str(len(packets)))
    
def matchdata(data):
    # 3a 04 00 00 00 00 00 00 00 ?? ?? 00 00 ?? 00 00 00
    start_matches = (
        data[0:2] == b'\x3A\x04' and
        data[2:9] == b'\x00\x00\x00\x00\x00\x00\x00'
    )
    return start_matches

def tryprint(raw_data):
    global capture
    global packets

    if not capture: return

    # 패킷 출력 방식
    printtohex = False
    printtostr = False
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
    
    #if len(raw_data) < 24: return # 길이 필터링
    #if not matchdata(raw_data): return # 헤더 필터링
    for x in blacklist:
        #if toutf16le(x) in raw_data: return # str 필터링
        ''
    # int 변환, hex보다 비교가 쪼끔 쉬움
    '''
    for i in range(0, len(raw_data), 4):
        chunk = raw_data[i:i+4]
        if len(chunk) == 4:
            int_val = struct.unpack('<I', chunk)[0]
            printint += f"{int_val} "
            valsint.append(int_val)
    '''
        
    #if valsint[2] in filterdata2: return #int 필터링

    if printtoint: print(printint)

    utf16list = utf16leprint(raw_data)
    if len(utf16list[0]) != 0 and printtostr:
        print((utf16list[0])) # str 데이터 출력
        ''
    
    if printtohex: print(raw_data.hex(" "))
    packets.append(raw_data)

def input_listener():
    global capture
    global packets
    global packetprocess
    session = PromptSession()

    # patch_stdout: print가 input을 침범하지 않도록 함
    with patch_stdout():
        while True:
            command = session.prompt("> ").strip()
            with capture_lock:
                if command.upper() == 'S': #stop
                    capture = False
                    print("[Capture stopped]")
                elif command.upper() == 'R': #start
                    capture = True
                    print("[Capture started]")
                elif command.upper() == 'E': #reset
                    packets = []
                    print("[Data resetted]")
                elif command.upper() == 'RE': #reset
                    capture = True
                    packets = []
                    print("[Data resetted]")
                elif command.isdigit():
                    value = int(command)
                    findinbytes(value.to_bytes(4, 'little'))
                elif command.upper() == 'Q': #exit
                    packetprocess = None # 종료를 위해 고의적으로 에러 발생, 정지 안되고 계속 돌아감;;
                    os._exit(0)

def processor():
    while True:
        data = packetprocess.get()
        tryprint(data)

def packet_callback(packet):
    if Raw in packet:
        #print(packet.summary())
        packetprocess.put(packet[Raw].load)
        #tryprint(packet[Raw].load)
                
input_thread = threading.Thread(target=input_listener, daemon=True)
input_thread.start()
pktprocess = threading.Thread(target=processor, daemon=True)
pktprocess.start()

print(f"STarting tcp port : {PORT}...")
sniff(filter=f"tcp port {PORT} and dst host {my_ip}", prn=packet_callback, store=0,)
#sniff(filter=f"tcp port {PORT}", prn=packet_callback, store=0)
