section .data
    prompt db 'Enter side length: ',0
    prompt_len equ $-prompt
    result_msg db 'Surface area: ',0
    result_msg_len equ $-result_msg
    newline db 10,0

section .bss
    side resb 16
    surface_area resb 16

section .text
    global _start

_start:
    ; Print prompt
    mov eax, 4
    mov ebx, 1
    mov ecx, prompt
    mov edx, prompt_len
    int 0x80

    ; Read input
    mov eax, 3
    mov ebx, 0
    mov ecx, side
    mov edx, 16
    int 0x80

    ; Convert input string to integer (simple, assumes valid input)
    mov ecx, side
    xor eax, eax        ; eax = 0 (result)
    xor ebx, ebx        ; ebx = 0 (digit)
.next_digit:
    mov bl, [ecx]
    cmp bl, 10          ; newline?
    je .done_input
    cmp bl, 13          ; carriage return?
    je .done_input
    cmp bl, 0
    je .done_input
    sub bl, '0'
    imul eax, eax, 10
    add eax, ebx
    inc ecx
    jmp .next_digit
.done_input:
    mov esi, eax        ; esi = side

    ; Calculate surface area: 6 * side * side
    mov eax, esi
    imul eax, esi       ; eax = side * side
    imul eax, 6         ; eax = 6 * side * side

    ; Convert result to string
    mov ebx, surface_area
    mov ecx, 0
    mov edi, ebx
    add edi, 15         ; point to end of buffer
    mov byte [edi], 0   ; null terminator
    dec edi
    cmp eax, 0
    jne .convert
    mov byte [edi], '0'
    dec edi
    jmp .print_result
.convert:
    mov edx, 0
.convert_loop:
    mov edx, 0
    div dword [ten]
    add dl, '0'
    mov [edi], dl
    dec edi
    cmp eax, 0
    jne .convert_loop

.print_result:
    inc edi

    ; Print result message
    mov eax, 4
    mov ebx, 1
    mov ecx, result_msg
    mov edx, result_msg_len
    int 0x80

    ; Print surface area
    mov eax, 4
    mov ebx, 1
    mov ecx, edi
    mov edx, surface_area
    add edx, 16
    sub edx, edi
    int 0x80

    ; Print newline
    mov eax, 4
    mov ebx, 1
    mov ecx, newline
    mov edx, 1
    int 0x80

    ; Exit
    mov eax, 1
    xor ebx, ebx
    int 0x80

section .data
    ten dd 10
