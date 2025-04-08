class WelcomeActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_welcome)
        
        val name = intent.getStringExtra("NAME") ?: "User"
        tvWelcome.text = "Welcome, $name!"
    }
}