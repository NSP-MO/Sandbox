section .data
    s dd 3              ; Side length (modify this value as needed)
    buffer db 10 dup(0) ; Buffer to store the result string

section .text
    global _start

_start:
    ; Calculate surface area (6 * s^2)
    mov eax, [s]        ; Load side length into EAX
    imul eax, eax       ; EAX = s^2
    imul eax, 6         ; EAX = 6 * s^2

    ; Convert result to ASCII string
    mov ecx, 10         ; Divisor for conversion
    mov edi, buffer + 9 ; Point to end of buffer
    xor edx, edx        ; Clear EDX

convert_loop:
    div ecx             ; Divide EAX by 10
    add dl, '0'         ; Convert remainder to ASCII
    mov [edi], dl       ; Store ASCII character
    dec edi             ; Move buffer pointer left
    xor edx, edx        ; Clear EDX for next division
    test eax, eax       ; Check if quotient is zero
    jnz convert_loop    ; Continue if not zero

    ; Prepare system call arguments
    inc edi             ; Adjust to first valid digit
    mov edx, buffer + 10
    sub edx, edi        ; Calculate string length
    mov esi, edi        ; Point to start of string

    ; Print result
    mov eax, 4          ; sys_write
    mov ebx, 1          ; stdout
    mov ecx, esi        ; String address
    int 0x80

    ; Exit program
    mov eax, 1          ; sys_exit
    xor ebx, ebx        ; Exit code 0
    int 0x80