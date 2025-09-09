import React, { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import { authAPI } from '../services/api';

interface User {
  id: number;
  email: string;
  username: string;
  first_name?: string;
  last_name?: string;
  is_active: boolean;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<boolean>;
  register: (userData: any) => Promise<boolean>;
  logout: () => void;
  setUser: (user: User) => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      if (token) {
        try {
          // Try to get current user from backend
          const response = await authAPI.getCurrentUser();
          setUser(response.data);
        } catch (error) {
          console.error('Failed to get current user on init, removing invalid token:', error);
          localStorage.removeItem('token');
          setToken(null);
        }
      }
      setLoading(false);
    };

    initAuth();
  }, [token]);

  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      const response = await authAPI.login(email, password);
      const { access_token } = response.data;
      
      localStorage.setItem('token', access_token);
      setToken(access_token);
      
      // Try to get actual user data from backend
      try {
        const userResponse = await authAPI.getCurrentUser();
        setUser(userResponse.data);
      } catch (userError) {
        console.error('Failed to get user data after login, using fallback:', userError);
        // Fallback to basic user info from login email
        const emailPart = email.split('@')[0];
        // Clean up email-derived username (remove numbers, capitalize)
        const cleanUsername = emailPart.replace(/\d+/g, '').toLowerCase();
        const displayName = cleanUsername.charAt(0).toUpperCase() + cleanUsername.slice(1);
        
        const fallbackUser: User = {
          id: 1,
          email: email,
          username: emailPart,
          first_name: displayName || 'User',
          last_name: '',
          is_active: true
        };
        setUser(fallbackUser);
      }
      
      return true;
    } catch (error) {
      console.error('Login failed:', error);
      return false;
    }
  };


  const register = async (userData: any): Promise<boolean> => {
    try {
      const response = await authAPI.register(userData);
      const { access_token } = response.data;
      
      localStorage.setItem('token', access_token);
      setToken(access_token);
      
      // Try to get actual user data from backend
      try {
        const userResponse = await authAPI.getCurrentUser();
        setUser(userResponse.data);
      } catch (userError) {
        console.error('Failed to get user data after registration, using registration data:', userError);
        // Use registration data as fallback
        const newUser: User = {
          id: 1,
          email: userData.email,
          username: userData.username,
          first_name: userData.first_name,
          last_name: userData.last_name,
          is_active: true
        };
        setUser(newUser);
      }
      
      return true;
    } catch (error) {
      console.error('Registration failed:', error);
      return false;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  };

  const value = {
    user,
    token,
    login,
    register,
    logout,
    setUser,
    loading,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
