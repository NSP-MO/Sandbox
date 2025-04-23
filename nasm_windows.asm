bits 32
global start

extern exit
extern printf
import exit msvcrt.dll
import printf msvcrt.dll

segment data use32 class=data
    fmt db "Surface area = %d", 10, 0 ; format string for printf
    side dd 4                        ; example side length
    area dd 0                        ; to store the result

segment code use32 class=code
start:
    mov eax, [side]      ; eax = side
    imul eax, eax        ; eax = side * side
    imul eax, 6          ; eax = 6 * side * side
    mov [area], eax      ; store result in area

    push dword [area]    ; push area for printf
    push dword fmt       ; push format string
    call [printf]
    add esp, 8           ; clean up stack

    push dword 0
    call [exit]