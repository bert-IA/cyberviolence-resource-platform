interface CardProps {
    title: string
    children: React.ReactNode
}

function Card({ title, children }: CardProps) {
    return (
        <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
            <h2 className="text-x1 font-bold mb-4 text-gray-800">{title}</h2>
            <div className="text-gray-600">{children}</div>
        </div>
    )

}
export default Card