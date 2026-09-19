import { motion } from 'framer-motion';

export function Reveal({ children, delay = 0, y = 28, ...rest }) {
    return (
        <motion.div
            initial={{ opacity: 0, y }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-60px' }}
            transition={{ duration: 0.4, delay, ease: [0.22, 1, 0.36, 1] }}
            {...rest}
        >
            {children}
        </motion.div>
    );
}

export function MaskLines({ lines, as: Tag = 'h1', className = '' }) {
    return (
        <Tag className={className} data-testid="hero-title">
            {lines.map((line, i) => (
                <span className="mask-line" key={i}>
                    <motion.span
                        initial={{ y: '112%' }}
                        animate={{ y: 0 }}
                        transition={{ duration: 0.4, delay: 0.08 + i * 0.08, ease: [0.22, 1, 0.36, 1] }}
                    >
                        {line}{i < lines.length - 1 ? ' ' : ''}
                    </motion.span>
                </span>
            ))}
        </Tag>
    );
}
