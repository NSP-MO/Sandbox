class UserViewModel(application: Application) : AndroidViewModel(application) {
    private val repository: UserRepository

    init {
        val userDao = AppDatabase.getDatabase(application).userDao()
        repository = UserRepository(userDao)
    }

    fun insert(user: User) = viewModelScope.launch {
        repository.insert(user)
    }

    fun getUserByEmail(email: String) = liveData {
        emit(repository.getUserByEmail(email))
    }

    fun login(email: String, password: String) = liveData {
        emit(repository.login(email, password))
    }
}