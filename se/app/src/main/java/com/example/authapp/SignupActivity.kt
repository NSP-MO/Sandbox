class SignupActivity : AppCompatActivity() {
    private lateinit var viewModel: UserViewModel
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_signup)

        viewModel = ViewModelProvider(this)[UserViewModel::class.java]

        btnSignup.setOnClickListener {
            val name = etName.text.toString().trim()
            val email = etEmail.text.toString().trim()
            val password = etPassword.text.toString().trim()
            val confirmPassword = etConfirmPassword.text.toString().trim()

            if (validateInput(name, email, password, confirmPassword)) {
                viewModel.getUserByEmail(email).observe(this) { existingUser ->
                    if (existingUser != null) {
                        showError("Email already registered")
                    } else {
                        val user = User(
                            name = name,
                            email = email,
                            password = password // Remember to hash in production!
                        )
                        viewModel.insert(user)
                        showSuccess("Registration successful!")
                        finish()
                    }
                }
            }
        }
    }

    private fun validateInput(name: String, email: String, password: String, confirmPassword: String): Boolean {
        // Add validation logic similar to login
        return true
    }
}