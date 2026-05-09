export const useUser = () => {
  const getUser = () => {
    try {
      return JSON.parse(localStorage.getItem('user') || '{}')
    } catch (err) {
      console.error('Error parsing user from localStorage', err)
      return {}
    }
  }

  const getFirstName = () => {
    const user = getUser()
    return user.first_name || user.username || ''
  }
const getLastName = () => {
    const user = getUser()
    return user.last_name || user.username || ''
  }

  const getEmail = () => {
    const user = getUser()
    return user.email || ''
  }

  const getUsername = () => {
    const user = getUser()
    return user.username || ''
  }

  const isLoggedIn = () => {
    const user = getUser()
    return !!user.id
  }

  return {
    getUser,
    getFirstName,
    getEmail,
    getUsername,
    isLoggedIn,
    getLastName
  }
}
