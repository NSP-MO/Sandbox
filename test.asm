section .data
    prompt      db "Enter the length of the cube's side: ", 0
    promptLen   equ $-prompt
    fmtIn       db "%lf", 0
    fmtOut      db "Surface area: %lf", 10, 0

section .bss
    side        resq 1
    area        resq 1

section .text
    extern  printf, scanf
    global  main

main:
    ; Print prompt
    mov     rdi, prompt
    xor     eax, eax
    call    printf

    ; Read input
    mov     rdi, fmtIn
    mov     rsi, side
    xor     eax, eax
    call    scanf

    ; Calculate area = 6 * side * side
    movsd   xmm0, qword [side]      ; xmm0 = side
    movsd   xmm1, xmm0              ; xmm1 = side
    mulsd   xmm0, xmm1              ; xmm0 = side * side
    movsd   xmm1, qword [six]       ; xmm1 = 6.0
    mulsd   xmm0, xmm1              ; xmm0 = 6 * side * side
    movsd   qword [area], xmm0

    ; Print result
    mov     rdi, fmtOut
    movsd   xmm0, qword [area]
    call    printf

    ; Return 0
    xor     eax, eax
    ret

section .data
six:    dq 6.0