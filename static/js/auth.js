// Gestionnaire d'authentification
class AuthManager {
    static async login(email, password) {
        try {
            const response = await fetch('/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password })
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || 'Erreur de connexion');
            }
            
            // Redirection vers le dashboard après connexion réussie
            window.location.href = '/dashboard';
            
        } catch (error) {
            console.error('Erreur de connexion:', error);
            throw error;
        }
    }

    static async register(userData) {
        try {
            const response = await fetch('/auth/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userData)
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || 'Erreur d\'inscription');
            }
            
            // Redirection vers la page de connexion après inscription réussie
            window.location.href = '/auth/login';
            
        } catch (error) {
            console.error('Erreur d\'inscription:', error);
            throw error;
        }
    }

    static async logout() {
        try {
            const response = await fetch('/auth/logout');
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || 'Erreur de déconnexion');
            }
            
            // Redirection vers la page d'accueil après déconnexion
            window.location.href = '/';
            
        } catch (error) {
            console.error('Erreur de déconnexion:', error);
            throw error;
        }
    }

    static async updateProfile(profileData) {
        try {
            const response = await fetch('/auth/profile/update', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(profileData)
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || 'Erreur de mise à jour du profil');
            }
            
            return data;
            
        } catch (error) {
            console.error('Erreur de mise à jour du profil:', error);
            throw error;
        }
    }

    static async getProfile() {
        try {
            const response = await fetch('/auth/profile');
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || 'Erreur de récupération du profil');
            }
            
            return data.user;
            
        } catch (error) {
            console.error('Erreur de récupération du profil:', error);
            throw error;
        }
    }
}

// Gestionnaire d'erreurs pour l'interface utilisateur
function showError(message, elementId = 'error-message') {
    const errorElement = document.getElementById(elementId);
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.style.display = 'block';
    } else {
        alert(message);
    }
}

// Gestionnaire de succès pour l'interface utilisateur
function showSuccess(message, elementId = 'success-message') {
    const successElement = document.getElementById(elementId);
    if (successElement) {
        successElement.textContent = message;
        successElement.style.display = 'block';
    }
}
