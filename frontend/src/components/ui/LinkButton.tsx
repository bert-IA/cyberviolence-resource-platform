import { NavLink } from "react-router-dom";

interface LinkButtonProps {
    to: string
    label: string
    variant?: 'primary' | 'secondary'
}

export function LinkButton({ to, label, variant = 'primary' }: LinkButtonProps) {
    const baseStyles = "px-6 py-3 rounded-lg font-semibold text-lg transition-all duration-200"


    const variantStyles = {
        // 🎨 Bouton non actif : semi-transparent sur fond vert
        primary: "bg-white/10 text-gray-600 hover:bg-white/20 hover:shadow-md",

        // 🎨 Alternative : boutons secondaires
        secondary: "bg-green-50 text-green-700 hover:bg-green-100"
    }[variant]

    return (
        <NavLink to={to} className={({ isActive }) =>
            `${baseStyles} ${variantStyles} ${isActive ? 'bg-purple-500 text-purple-500 font-bold shadow-lg ring-2 ring-purple-500'
                : ''}`}>
            {label}
        </NavLink>
    )
}