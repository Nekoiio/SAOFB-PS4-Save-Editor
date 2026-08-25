from Classes.Save    import *
# Init
KNOWN_MARKER: bytes = b"Gamepad_RightY"
KNOWN_MARKER_LENGTH: int = 0x0F

test: bytes = bytes.fromhex(
    "0d0000004143433030365f3030365f4300010000000000000003cf0100000a0000000000000000000000000000000000000000000000000004000000040000001c3d9b153e211ea7e83d18976e923d1d6ff0853d"
)

AccT: Equipment = Equipment(test, 0, "A")

data: bytes = b""
with open("SAOFBS/ue4savegame.ps4.sav", "rb")as f: data = f.read()

start_offset: int =  data[:0x2000].find(KNOWN_MARKER)
start_offset += (KNOWN_MARKER_LENGTH + 4) * 2


















"""
Read up to 0x2000 and check for b"Gamepad_RightY" + int





asm4:
        <+0>:   endbr32
        <+4>:   push   ebp
        <+5>:   mov    ebp,esp
        <+7>:   push   ebx
        <+8>:   sub    esp,0x10
        <+11>:  mov    DWORD PTR [ebp-0x10],0x254
        <+18>:  mov    DWORD PTR [ebp-0xc],0x0
        <+25>:  jmp    0x11cc <asm4+31>
        LABEL_01:
        <+27>:  add    DWORD PTR [ebp-0xc],0x1
        <+31>:  mov    edx,DWORD PTR [ebp-0xc]
        <+34>:  mov    eax,DWORD PTR [ebp+0x8]
        <+37>:  add    eax,edx
        <+39>:  movzx  eax,BYTE PTR [eax]
        <+42>:  test   al,al
        <+44>:  jne    LABEL_01
        <+46>:  mov    DWORD PTR [ebp-0x8],0x1
        <+53>:  jmp    0x123b <asm4+142>
        <+55>:  mov    edx,DWORD PTR [ebp-0x8]
        <+58>:  mov    eax,DWORD PTR [ebp+0x8]
        <+61>:  add    eax,edx
        <+63>:  movzx  eax,BYTE PTR [eax]
        <+66>:  movsx  edx,al
        <+69>:  mov    eax,DWORD PTR [ebp-0x8]
        <+72>:  lea    ecx,[eax-0x1]
        <+75>:  mov    eax,DWORD PTR [ebp+0x8]
        <+78>:  add    eax,ecx
        <+80>:  movzx  eax,BYTE PTR [eax]
        <+83>:  movsx  eax,al
        <+86>:  sub    edx,eax
        <+88>:  mov    eax,edx
        <+90>:  mov    edx,eax
        <+92>:  mov    eax,DWORD PTR [ebp-0x10]
        <+95>:  lea    ebx,[edx+eax*1]
        <+98>:  mov    eax,DWORD PTR [ebp-0x8]
        <+101>: lea    edx,[eax+0x1]
        <+104>: mov    eax,DWORD PTR [ebp+0x8]
        <+107>: add    eax,edx
        <+109>: movzx  eax,BYTE PTR [eax]
        <+112>: movsx  edx,al
        <+115>: mov    ecx,DWORD PTR [ebp-0x8]
        <+118>: mov    eax,DWORD PTR [ebp+0x8]
        <+121>: add    eax,ecx
        <+123>: movzx  eax,BYTE PTR [eax]
        <+126>: movsx  eax,al
        <+129>: sub    edx,eax
        <+131>: mov    eax,edx
        <+133>: add    eax,ebx
        <+135>: mov    DWORD PTR [ebp-0x10],eax
        <+138>: add    DWORD PTR [ebp-0x8],0x1
        <+142>: mov    eax,DWORD PTR [ebp-0xc]
        <+145>: sub    eax,0x1
        <+148>: cmp    DWORD PTR [ebp-0x8],eax
        <+151>: jl     0x11e4 <asm4+55>
        <+153>: mov    eax,DWORD PTR [ebp-0x10]
        <+156>: add    esp,0x10
        <+159>: pop    ebx
        <+160>: pop    ebp
        <+161>: ret

"""