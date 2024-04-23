import React, {useState, useEffect} from 'react';
import './animation.css';

const FadeInOut: React.FC<{ children: React.ReactNode }> = (
    {children}) => {
    const [show, setShow] = useState(false);

    useEffect(() => {
        setShow(true);
    }, []);

    const renderAnimation = () => {
            return <div className={`fade-in-three ${show ? 'scale-animation' : ''}`}>{children}</div>;
    };

    return (
        <React.Fragment>
            {renderAnimation()}
        </React.Fragment>
    );
};

export default FadeInOut;
