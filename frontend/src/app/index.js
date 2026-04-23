import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from '../components/layout/Header';
import Footer from '../components/layout/Footer';
import EventsPage from '../pages/EventsPage';
import EventDetailPage from '../pages/EventDetailPage';
import ProfilePage from '../pages/ProfilePage';
import LoginPage from '../pages/LoginPage';
import RegisterPage from '../pages/RegisterPage';
import SelectInterestsPage from '../pages/SelectInterestsPage';
import EditProfilePage from '../pages/EditProfilePage';
import '../styles/global.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Header />
        <main style={{ minHeight: '80vh' }}>
          <Routes>
            {/* Главная страница - события */}
            <Route path="/" element={<EventsPage />} />
            
            {/* Детали события */}
            <Route path="/events/:id" element={<EventDetailPage />} />
            
            {/* Личный кабинет */}
            <Route path="/profile" element={<ProfilePage />} />
            
            {/* Редактирование профиля */}
            <Route path="/profile/edit" element={<EditProfilePage />} />
            
            {/* Авторизация */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/select-interests" element={<SelectInterestsPage />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  );
}

export default App;
