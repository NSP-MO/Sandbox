section .data
    s           dd 3              ; Side length
    buffer      db 10 dup(0)        ; Buffer to store the result string
    numWritten  dd 0                ; For WriteConsoleA to return count

section .text
global mainCRTStartup
extern GetStdHandle
extern WriteConsoleA
extern ExitProcess

mainCRTStartup:
    ; Calculate surface area: 6 * s^2
    mov eax, [s]          ; Load side length into EAX
    imul eax, eax         ; EAX = s^2
    imul eax, 6           ; EAX = 6 * s^2
    ; Result is in EAX; for conversion we use RAX

    mov rcx, 10           ; Divisor (10)
    lea rdi, [buffer+9]   ; RDI points to end of buffer
    xor rdx, rdx          ; Clear RDX

convert_loop:
    div rcx               ; Divide RAX by 10; quotient in RAX, remainder in RDX
    add dl, '0'           ; Convert remainder to ASCII
    mov [rdi], dl         ; Store the converted digit
    dec rdi              ; Move pointer backwards
    xor rdx, rdx         ; Clear RDX for next division
    test rax, rax        ; Check if quotient is zero
    jnz convert_loop     ; Continue if not zero
    inc rdi              ; Adjust pointer to first valid digit

    ; Calculate string length = (buffer+10) - rdi
    lea r8, [buffer+10]
    sub r8, rdi         ; r8 now holds the length

    ; Get handle to stdout (STD_OUTPUT_HANDLE = -11)
    mov ecx, -11        ; First parameter in RCX
    call GetStdHandle   ; Returned handle in RAX

    ; Write the string to the console
    ; Windows x64 calling: RCX: handle, RDX: lpBuffer, R8: nNumberOfCharsToWrite, R9: lpNumberOfCharsWritten
    mov rcx, rax        ; hConsoleOutput
    mov rdx, rdi        ; Pointer to the string
    ; r8: length already computed
    lea r9, [rel numWritten] ; Address for number of characters written
    call WriteConsoleA

    ; Exit process with exit code 0
    mov ecx, 0          ; Exit code in RCX
    call ExitProcess