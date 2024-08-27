import React, { useState } from 'react';
import PropTypes from 'prop-types';

/**
 * CustomButton is an example component that shows a bouncing button.
 */
const CustomButton = (props) => {
    // Extract the props
    const { id, label, color, className } = props;
    const [isBouncing, setIsBouncing] = useState(false);

    // Handle the button click event
    const handleClick = () => {
        setIsBouncing(true);
        setTimeout(() => setIsBouncing(false), 500);  // Reset after animation
    };

    // Determine Bootstrap color class based on the color prop
    const colorClass = color ? `btn-${color}` : '';

    // Render the button
    return (
        <button
            id={id}
            onClick={handleClick}
            className={`btn ${colorClass} ${className} ${isBouncing ? 'bouncing' : ''}`}
            style={{
                padding: '10px 20px',
                border: 'none',
                borderRadius: '5px',
                backgroundColor: color ? '' : '#ff8c00',  // Custom fallback color if no Bootstrap color is provided
                color: 'white',
                fontSize: '16px',
                cursor: 'pointer',
                outline: 'none',
                position: 'relative',
                transition: 'transform 0.3s ease',
                transform: isBouncing ? 'translateY(-10px)' : 'translateY(0)',
            }}
        >
            {label}
        </button>
    );
}

CustomButton.propTypes = {
    /**
     * The ID used to identify this component in Dash callbacks.
     */
    id: PropTypes.string,

    /**
     * A label that will be printed when this component is rendered.
     */
    label: PropTypes.string.isRequired,

    /**
     * The color of the button.
     * This should be a Bootstrap color name.
     */
    color: PropTypes.string,

    /**
     * The className of the button.
     * This is used to apply custom styles to the button.
     */
    className: PropTypes.string,
};

export default CustomButton;
