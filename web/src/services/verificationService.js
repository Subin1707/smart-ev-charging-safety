import { BRIDGE_BASE_URL } from '../config/simulationMode'

async function request(path, options) {
	const response = await fetch(`${BRIDGE_BASE_URL}${path}`, options)
	if (!response.ok) throw new Error(await response.text())
	return response.json()
}

export function getVerificationSummary() {
	return request('/api/verification/summary')
}

export function getVerificationRequirements() {
	return request('/api/verification/requirements')
}

export function verifySpecification(file) {
	const body = new FormData()
	body.append('file', file)
	return request('/api/specification/verify', { method: 'POST', body })
}

export function getRequirementEvidence(requirementId) {
	return request(`/api/verification/requirements/${encodeURIComponent(requirementId)}/evidence`)
}
