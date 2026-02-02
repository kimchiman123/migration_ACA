import React from 'react';

const Skeleton = ({ className }) => {
    return (
        <div className={`animate-pulse bg-[color:var(--surface-muted)] rounded-xl ${className}`} />
    );
};

export default Skeleton;
