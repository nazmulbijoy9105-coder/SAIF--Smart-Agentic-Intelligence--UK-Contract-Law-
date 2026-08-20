"use client";
import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL;
const api = axios.create({ baseURL: API_URL, headers: { "Content-Type": "application/json" }, timeout: 120000 });
api.interceptors.request.use((config) => { if (typeof window !== "undefined") { const token = localStorage.getItem("saif_token"); if (token) { config.headers = config.headers || {}; config.headers.Authorization = `Bearer ${token}`; } } return config; });

export type ContractCategory = "B2B" | "B2C";
export type BargainingPower = "equal" | "unequal" | "unknown";
export type EvidenceQuality = "weak" | "standard" | "strong";
export type NoticeObjectiveStatus = "adequate" | "inadequate" | "buried" | "not_given" | "unknown";

export interface PaymentFacts { invoiceNumber?: string | null; invoiceDate?: string | null; dueDate?: string | null; invoiceAmount: number; amountPaid: number; amountWithheld: number; withholdingReason?: string | null; contractualWithholdingRight?: boolean | null; contractualSetOffRight?: boolean | null; statutoryWithholdingBasis?: string | null; }
export interface DefectFacts { alleged: boolean; defectiveUnits: number; totalUnits: number; description?: string | null; inspectionReports: string[]; photographs: string[]; technicalEvidence: string[]; specification?: string | null; rejectionCommunicated?: boolean | null; }
export interface TerminationFacts { clauseExists: boolean; noticeDate?: string | null; noticeReceivedDate?: string | null; curePeriodDays?: number | null; terminationDate?: string | null; reservationOfRights?: boolean | null; continuedPerformanceAfterBreach: boolean; }
export interface LossFacts { directLoss?: number | null; lostProfits?: number | null; consequentialLoss?: number | null; communicatedAtFormation?: boolean | null; }
export interface LimitationFacts { clauseText?: string | null; excludesLiability: boolean; capsLiability: boolean; liabilityType?: string | null; unusualOrOnerousTerm: boolean; }
export interface DisputeInput { claimant:string; defendant:string; contractType:string; contractCategory:ContractCategory; value:number; summary:string; disputedClause?:string; standardForm:boolean; bargainingPower:BargainingPower; bargainingSubjectiveBelief?:string; noticeObjectiveStatus:NoticeObjectiveStatus; noticeSubjectiveBelief?:string; allowsUnilateralVariation:boolean; consumerVulnerable:boolean; evidenceQuality:EvidenceQuality; payment?:PaymentFacts; defect?:DefectFacts; termination?:TerminationFacts; loss?:LossFacts; limitation?:LimitationFacts; contractualInterestRate?:number|null; signedDocument?:boolean; unusualOrOnerousTerm:boolean; phase:number; }
export interface AssessmentResult { success:boolean; data:any; assessment_id:string; phase:number; }

export const createDefaultPaymentFacts = ():PaymentFacts => ({ invoiceNumber:null, invoiceDate:null, dueDate:null, invoiceAmount:0, amountPaid:0, amountWithheld:0, withholdingReason:null, contractualWithholdingRight:null, contractualSetOffRight:null, statutoryWithholdingBasis:null });
export const createDefaultDefectFacts = ():DefectFacts => ({ alleged:false, defectiveUnits:0, totalUnits:0, description:null, inspectionReports:[], photographs:[], technicalEvidence:[], specification:null, rejectionCommunicated:null });
export const createDefaultTerminationFacts = ():TerminationFacts => ({ clauseExists:false, noticeDate:null, noticeReceivedDate:null, curePeriodDays:null, terminationDate:null, reservationOfRights:null, continuedPerformanceAfterBreach:false });
export const createDefaultLossFacts = ():LossFacts => ({ directLoss:null, lostProfits:null, consequentialLoss:null, communicatedAtFormation:null });
export const createDefaultLimitationFacts = ():LimitationFacts => ({ clauseText:null, excludesLiability:false, capsLiability:false, liabilityType:null, unusualOrOnerousTerm:false });

export async function submitAssessment(input:DisputeInput):Promise<AssessmentResult> { const res=await api.post<AssessmentResult>("/assess/", {...input, payment:input.payment??createDefaultPaymentFacts(), defect:input.defect??createDefaultDefectFacts(), termination:input.termination??createDefaultTerminationFacts(), loss:input.loss??createDefaultLossFacts(), limitation:input.limitation??createDefaultLimitationFacts()}); return res.data; }
export async function quickAssess(input:DisputeInput):Promise<AssessmentResult> { const res=await api.post<AssessmentResult>("/assess/quick", input); return res.data; }
export async function getHealth(){ const res=await api.get("/health/"); return res.data; }
export function getApiErrorMessage(error:unknown){ if(axios.isAxiosError(error)){ return error.response?.data?.detail || error.message || "SAIF API request failed."; } return error instanceof Error ? error.message : "Unexpected SAIF error."; }
export default api;
