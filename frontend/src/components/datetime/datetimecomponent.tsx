import React, { useState, useEffect } from 'react';
import './datetimecomponent.css'
const DateTimeComponent = () => {
    const [currentDateTime, setCurrentDateTime] = useState(new Date());

    useEffect(() => {
        const timer = setInterval(() => {
            setCurrentDateTime(new Date());
        }, 1000);

        return () => {
            clearInterval(timer);
        };
    }, []);

    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    const dayOfWeek = days[currentDateTime.getDay()];

    return (
        <div className={'datetime-main'}>
            <span className={'datetime'}>{currentDateTime.toLocaleString()}</span>
            <span className={'datetime'}>{dayOfWeek}</span>
        </div>
    );
};

export default DateTimeComponent;
