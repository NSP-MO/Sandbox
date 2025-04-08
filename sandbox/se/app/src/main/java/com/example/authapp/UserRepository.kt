class UserRepository(private val userDao: UserDao) {
    suspend fun insert(user: User) = userDao.insert(user)
    suspend fun getUserByEmail(email: String) = userDao.getUserByEmail(email)
    suspend fun login(email: String, password: String) = userDao.login(email, password)
}