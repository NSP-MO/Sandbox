section .data
    s dd 3              ; Side length (modify this value as needed)
    buffer db 10 dup(0) ; Buffer to store the result string
    msg db "Surface area: ", 0

section .bss

section .text
    extern printf
    extern exit
    global main

main:
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

    ; Print result
    inc edi             ; Adjust to first valid digit
    mov rsi, edi        ; Point to start of string
    mov rdi, msg        ; Load message string
    xor eax, eax        ; Clear EAX for printf
    call printf         ; Call printf

    ; Exit program
    xor edi, edi        ; Exit code 0
    call exit
