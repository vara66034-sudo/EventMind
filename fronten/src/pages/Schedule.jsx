import React, { useState, useEffect } from 'react';
import { scheduleAPI } from '../api/schedule';
import { format, addDays, startOfWeek, parseISO } from 'date-fns';
import { ru } from 'date-fns/locale';

const Schedule = () => {
    const [schedule, setSchedule] = useState({});
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [showForm, setShowForm] = useState(false);
    const [formData, setFormData] = useState({
        date: '',
        startTime: '10:00',
        endTime: '12:00',
        title: ''
    });
    const [currentWeekStart, setCurrentWeekStart] = useState(startOfWeek(new Date(), { weekStartsOn: 1 })); // понедельник

    const fetchSchedule = async (startDate) => {
        setLoading(true);
        try {
            const result = await scheduleAPI.getSchedule(startDate.toISOString());
            if (result.success) {
                setSchedule(result.data);
            } else {
                setError(result.error || 'Ошибка загрузки расписания');
            }
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchSchedule(currentWeekStart);
    }, [currentWeekStart]);

    const handlePrevWeek = () => {
        setCurrentWeekStart(prev => addDays(prev, -7));
    };

    const handleNextWeek = () => {
        setCurrentWeekStart(prev => addDays(prev, 7));
    };

    const handleInputChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleAddSlot = async (e) => {
        e.preventDefault();
        const { date, startTime, endTime, title } = formData;
        if (!date || !startTime || !endTime) {
            setError('Заполните дату, время начала и окончания');
            return;
        }
        const startDateTime = `${date}T${startTime}:00`;
        const endDateTime = `${date}T${endTime}:00`;
        try {
            const result = await scheduleAPI.addBusySlot(startDateTime, endDateTime, title || 'Занято');
            if (result.success) {
                setShowForm(false);
                setFormData({ date: '', startTime: '10:00', endTime: '12:00', title: '' });
                fetchSchedule(currentWeekStart);
            } else {
                setError(result.error || 'Ошибка добавления');
            }
        } catch (err) {
            setError(err.message);
        }
    };

    // Создаём массив дней текущей недели
    const weekDays = [];
    for (let i = 0; i < 7; i++) {
        const day = addDays(currentWeekStart, i);
        weekDays.push(day);
    }

    return (
        <div className="max-w-4xl mx-auto p-6">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold">Моё расписание</h1>
                <button
                    onClick={() => setShowForm(!showForm)}
                    className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700"
                >
                    {showForm ? 'Отмена' : '+ Добавить занятость'}
                </button>
            </div>

            {error && (
                <div className="bg-red-100 text-red-600 p-3 rounded mb-4">
                    {error}
                </div>
            )}

            {/* Форма добавления занятости */}
            {showForm && (
                <form onSubmit={handleAddSlot} className="bg-white p-4 rounded shadow mb-6">
                    <h2 className="text-lg font-semibold mb-3">Новая занятость</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Дата</label>
                            <input
                                type="date"
                                name="date"
                                value={formData.date}
                                onChange={handleInputChange}
                                className="w-full px-3 py-2 border rounded"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Время начала</label>
                            <input
                                type="time"
                                name="startTime"
                                value={formData.startTime}
                                onChange={handleInputChange}
                                className="w-full px-3 py-2 border rounded"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Время окончания</label>
                            <input
                                type="time"
                                name="endTime"
                                value={formData.endTime}
                                onChange={handleInputChange}
                                className="w-full px-3 py-2 border rounded"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Название (опционально)</label>
                            <input
                                type="text"
                                name="title"
                                value={formData.title}
                                onChange={handleInputChange}
                                placeholder="Например: Работа, Встреча"
                                className="w-full px-3 py-2 border rounded"
                            />
                        </div>
                    </div>
                    <div className="mt-4 flex justify-end">
                        <button
                            type="submit"
                            className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
                        >
                            Добавить
                        </button>
                    </div>
                </form>
            )}

            {/* Навигация по неделям */}
            <div className="flex justify-between items-center mb-4">
                <button onClick={handlePrevWeek} className="px-3 py-1 border rounded hover:bg-gray-100">
                    ← Предыдущая
                </button>
                <span className="text-lg font-medium">
                    {format(currentWeekStart, 'd MMMM', { locale: ru })} — {format(addDays(currentWeekStart, 6), 'd MMMM yyyy', { locale: ru })}
                </span>
                <button onClick={handleNextWeek} className="px-3 py-1 border rounded hover:bg-gray-100">
                    Следующая →
                </button>
            </div>

            {loading ? (
                <div className="text-center py-8">Загрузка...</div>
            ) : (
                <div className="grid grid-cols-7 gap-2">
                    {weekDays.map(day => {
                        const dateStr = format(day, 'yyyy-MM-dd');
                        const slots = schedule[dateStr] || [];
                        return (
                            <div key={dateStr} className="border rounded p-2 min-h-[200px]">
                                <div className="font-bold text-center mb-2">
                                    {format(day, 'EEEE', { locale: ru })}
                                    <br />
                                    <span className="text-sm text-gray-500">{format(day, 'd MMM', { locale: ru })}</span>
                                </div>
                                <div className="space-y-1">
                                    {slots.map((slot, idx) => (
                                        <div key={idx} className="text-xs bg-gray-100 p-1 rounded">
                                            <div className="font-medium">{slot.title}</div>
                                            <div className="text-gray-500">
                                                {slot.start.substring(11, 16)} - {slot.end.substring(11, 16)}
                                            </div>
                                        </div>
                                    ))}
                                    {slots.length === 0 && (
                                        <div className="text-xs text-gray-400 text-center mt-4">Свободно</div>
                                    )}
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
};

export default Schedule;
