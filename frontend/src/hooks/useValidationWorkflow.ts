import { useReducer, type Dispatch } from "react"

export interface ValidationStepProps {
    state: ValidationState
    dispatch: Dispatch<ValidationAction>
}

type validationStep = 'overview' | 'review'

type FilterType = {
    country?: string
    category?: string
}

export type ValidationState = {
    step: validationStep
    filter: FilterType
    selectedIds: string[]
    groupBy: 'country' | 'category' | 'all'
}

// 🆕 Export pour utilisation dans d'autres composants
export type ValidationAction =
    | { type: 'SELECT_COUNTRY'; country: string }
    | { type: 'SELECT_CATEGORY'; category: string }
    | { type: 'SHOW_ALL' }
    | { type: 'BACK_TO_OVERVIEW' }
    | { type: 'TOGGLE_SELECTION'; id: string }
    | { type: 'SELECT_ALL'; ids: string[] }
    | { type: 'CLEAR_SELECTION' }

function validationReducer(
    state: ValidationState,
    action: ValidationAction
): ValidationState {
    switch (action.type) {
        case 'SELECT_COUNTRY':
            return {
                ...state,
                step: 'review',
                filter: { country: action.country },
                groupBy: 'country',
                selectedIds: [],
            }

        case 'SELECT_CATEGORY':
            return {
                ...state,
                step: 'review',
                filter: { category: action.category },
                groupBy: 'category',
                selectedIds: [],
            }

        case 'SHOW_ALL':
            return {
                ...state,
                step: 'review',
                filter: {},
                groupBy: 'all',
                selectedIds: [],
            }

        case 'BACK_TO_OVERVIEW':
            return {
                ...state,
                step: 'overview',
                filter: {},
                selectedIds: [],
            }

        case 'TOGGLE_SELECTION':
            return {
                ...state,
                selectedIds: state.selectedIds.includes(action.id)
                    ? state.selectedIds.filter(id => id !== action.id)
                    : [...state.selectedIds, action.id],
            }

        case 'SELECT_ALL':
            return {
                ...state,
                selectedIds: action.ids,
            }

        case 'CLEAR_SELECTION':
            return {
                ...state,
                selectedIds: [],
            }

        default:
            return state
    }
}

// === HOOK ===

export function useValidationWorkflow() {
    const [state, dispatch] = useReducer(validationReducer, {
        step: 'overview',
        filter: {},
        selectedIds: [],
        groupBy: 'all',
    })

    return { state, dispatch }
}