import { BINDING_FAMILY_MATRIX, FAMILY_SUBEVENT_MATRIX, BINDING_SUBEVENT_MATRIX } from "./registry";

export function bindingSupportsFamily(binding: keyof typeof BINDING_FAMILY_MATRIX, family: string): boolean {
  return (BINDING_FAMILY_MATRIX as any)[binding][family] !== "F";
}

export function familySupportsSubevent(family: keyof typeof FAMILY_SUBEVENT_MATRIX, subevent: string): boolean {
  return ((FAMILY_SUBEVENT_MATRIX as any)[family] ?? {})[subevent] !== "F";
}

export function bindingSupportsSubevent(binding: keyof typeof BINDING_SUBEVENT_MATRIX, subevent: string): boolean {
  return ((BINDING_SUBEVENT_MATRIX as any)[binding] ?? {})[subevent] !== "F";
}
