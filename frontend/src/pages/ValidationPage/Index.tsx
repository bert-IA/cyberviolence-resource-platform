// frontend/src/pages/ValidationPage/index.tsx

import { useValidationWorkflow } from '../../hooks/useValidationWorkflow'  // ← Après renommage
import { OverviewStep } from './OverviewStep'
import { ReviewStep } from './ReviewStep'



export function ValidationPage() {
    const { state, dispatch } = useValidationWorkflow()

    return state.step === 'overview' ? (
        <OverviewStep
            state={state}
            dispatch={dispatch}
        />
    ) : (
        <ReviewStep
            state={state}
            dispatch={dispatch}
        />
    )
}