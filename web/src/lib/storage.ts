import { supabase } from './supabase'

export type UploadResult = {
  url: string
  path: string
}

export class StorageService {
  static async uploadProjectImage(
    userId: string,
    projectId: string,
    file: File
  ): Promise<UploadResult> {
    const fileExt = file.name.split('.').pop()
    const fileName = `${Date.now()}.${fileExt}`
    const filePath = `${userId}/${projectId}/${fileName}`

    const { data, error } = await supabase.storage
      .from('project-images')
      .upload(filePath, file, {
        contentType: file.type,
        upsert: false,
      })

    if (error) {
      throw new Error(`Upload failed: ${error.message}`)
    }

    const { data: { publicUrl } } = supabase.storage
      .from('project-images')
      .getPublicUrl(filePath)

    return {
      url: publicUrl,
      path: filePath,
    }
  }

  static async uploadProjectDocument(
    userId: string,
    projectId: string,
    file: File
  ): Promise<UploadResult> {
    const fileExt = file.name.split('.').pop()
    const fileName = `${Date.now()}-${file.name}`
    const filePath = `${userId}/${projectId}/${fileName}`

    const { data, error } = await supabase.storage
      .from('project-documents')
      .upload(filePath, file, {
        contentType: file.type,
        upsert: false,
      })

    if (error) {
      throw new Error(`Upload failed: ${error.message}`)
    }

    const { data: { publicUrl } } = supabase.storage
      .from('project-documents')
      .getPublicUrl(filePath)

    return {
      url: publicUrl,
      path: filePath,
    }
  }

  static async deleteFile(bucket: string, path: string): Promise<void> {
    const { error } = await supabase.storage
      .from(bucket)
      .remove([path])

    if (error) {
      throw new Error(`Delete failed: ${error.message}`)
    }
  }

  static async uploadProfileImage(
    userId: string,
    file: File
  ): Promise<UploadResult> {
    const fileExt = file.name.split('.').pop()
    const fileName = `avatar.${fileExt}`
    const filePath = `${userId}/${fileName}`

    const { data, error } = await supabase.storage
      .from('profile-images')
      .upload(filePath, file, {
        contentType: file.type,
        upsert: true, // Replace existing avatar
      })

    if (error) {
      throw new Error(`Upload failed: ${error.message}`)
    }

    const { data: { publicUrl } } = supabase.storage
      .from('profile-images')
      .getPublicUrl(filePath)

    return {
      url: publicUrl,
      path: filePath,
    }
  }

  // Helper to convert File to base64 for sending to backend
  static async fileToBase64(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.readAsDataURL(file)
      reader.onload = () => resolve(reader.result as string)
      reader.onerror = (error) => reject(error)
    })
  }

  // Helper to validate file size and type
  static validateImage(file: File, maxSizeMB: number = 5): string | null {
    const maxSize = maxSizeMB * 1024 * 1024 // Convert to bytes
    
    if (file.size > maxSize) {
      return `File size must be less than ${maxSizeMB}MB`
    }

    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
    if (!allowedTypes.includes(file.type)) {
      return 'File must be a JPEG, PNG, or WebP image'
    }

    return null
  }
}