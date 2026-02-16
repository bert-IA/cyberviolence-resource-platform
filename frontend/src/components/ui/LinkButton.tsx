import type { ReactNode } from "react";
import { NavLink } from "react-router-dom";

interface LinkButtonProps {
    to: string
    label: string
    variant?: 'primary' | 'secondary' | 'sidebar'
    icon?: ReactNode
}

export function LinkButton({
    to,
    label,
    variant = 'primary',
    icon
}: LinkButtonProps) {
    const baseStyles = "rounded-lg font-semibold text-lg transition-all duration-200"


    const variantStyles = {
        // 🎨 Pour Header horizontal (ton usage actuel)
        primary: "px-6 py-3 text-lg bg-white/10 text-gray-600 hover:bg-white/20 hover:shadow-md",

        // 🎨 Boutons secondaires Header
        secondary: "px-6 py-3 text-lg bg-green-50 text-green-700 hover:bg-green-100",

        // 🎨 NOUVEAU : Pour Sidebar verticale
        sidebar: "flex items-center gap-3 px-4 py-3 text-gray-700 hover:bg-gray-100"
    }[variant]

    const activeStyles = {
        primary: 'bg-purple-500 text-white font-bold shadow-lg ring-2 ring-purple-500',
        secondary: 'bg-green-200 text-green-900',
        sidebar: 'bg-purple-100 text-purple-700 font-semibold'  // ← Style actif Sidebar
    }[variant]

    return (
        <NavLink
            to={to}
            className={({ isActive }) =>
                `${baseStyles} ${variantStyles} ${isActive ? activeStyles : ''}`
            }
        >
            {/* Afficher icône si fournie (pour Sidebar) */}
            {icon && <span className="text-2xl">{icon}</span>}
            {label}
        </NavLink>
    )
}