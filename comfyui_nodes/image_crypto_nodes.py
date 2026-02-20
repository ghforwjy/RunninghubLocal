"""
ComfyUI 图片加密/解密节点
支持密码保护，完全在节点内完成加解密
"""

import torch
import numpy as np
from PIL import Image
import hashlib


class ImageEncryptNode:
    """
    图片加密节点
    使用密码对图片进行像素级加密，生成不可识别的乱码图
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),  # 输入图片
                "password": ("STRING", {"default": "", "multiline": False}),  # 加密密码
                "encrypt_mode": (["XOR", "SHUFFLE", "COMBINE"], {"default": "COMBINE"}),  # 加密模式
                "noise_strength": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.01}),  # 额外噪声强度
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("encrypted_image",)
    FUNCTION = "encrypt_image"
    CATEGORY = "image/crypto"
    
    def encrypt_image(self, image, password, encrypt_mode, noise_strength):
        """
        加密图片
        
        Args:
            image: 输入图片 tensor [B, H, W, C]
            password: 加密密码
            encrypt_mode: 加密模式 (XOR/SHUFFLE/COMBINE)
            noise_strength: 额外噪声强度
        
        Returns:
            加密后的图片 tensor
        """
        # 转换为 numpy 数组
        img_np = image.cpu().numpy()
        batch_size, height, width, channels = img_np.shape
        
        # 使用密码生成随机种子
        seed = self._password_to_seed(password)
        np.random.seed(seed)
        
        encrypted_batch = []
        
        for b in range(batch_size):
            img = img_np[b].copy()  # [H, W, C]
            
            if encrypt_mode in ["XOR", "COMBINE"]:
                img = self._xor_encrypt(img, seed + b)
            
            if encrypt_mode in ["SHUFFLE", "COMBINE"]:
                img = self._shuffle_encrypt(img, seed + b)
            
            # 添加可选噪声
            if noise_strength > 0:
                noise = np.random.randn(*img.shape) * noise_strength
                img = np.clip(img + noise, 0, 1)
            
            encrypted_batch.append(img)
        
        # 转换回 tensor
        encrypted_np = np.stack(encrypted_batch, axis=0)
        encrypted_tensor = torch.from_numpy(encrypted_np).float()
        
        return (encrypted_tensor,)
    
    def _password_to_seed(self, password):
        """将密码转换为随机种子"""
        if not password:
            return 42  # 默认种子
        hash_obj = hashlib.md5(password.encode('utf-8'))
        return int(hash_obj.hexdigest(), 16) % (2**32)
    
    def _xor_encrypt(self, img, seed):
        """异或加密 - 对像素值进行变换"""
        np.random.seed(seed)
        
        # 生成与图片形状相同的密钥矩阵
        key = np.random.randint(0, 256, size=img.shape, dtype=np.uint8) / 255.0
        
        # 异或操作 (在浮点数域中进行)
        encrypted = np.abs(img - key)
        encrypted = np.clip(encrypted, 0, 1)
        
        return encrypted
    
    def _shuffle_encrypt(self, img, seed):
        """置换加密 - 打乱像素位置"""
        np.random.seed(seed)
        h, w, c = img.shape
        
        # 生成像素索引的随机置换
        indices = np.arange(h * w)
        np.random.shuffle(indices)
        
        # 重塑图片并应用置换
        img_flat = img.reshape(-1, c)
        shuffled = img_flat[indices]
        
        return shuffled.reshape(h, w, c)


class ImageDecryptNode:
    """
    图片解密节点
    使用正确的密码还原被加密的图片
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "encrypted_image": ("IMAGE",),  # 加密后的图片
                "password": ("STRING", {"default": "", "multiline": False}),  # 解密密码
                "encrypt_mode": (["XOR", "SHUFFLE", "COMBINE"], {"default": "COMBINE"}),  # 加密模式（必须与加密时一致）
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("decrypted_image",)
    FUNCTION = "decrypt_image"
    CATEGORY = "image/crypto"
    
    def decrypt_image(self, encrypted_image, password, encrypt_mode):
        """
        解密图片
        
        Args:
            encrypted_image: 加密后的图片 tensor [B, H, W, C]
            password: 解密密码
            encrypt_mode: 加密模式（必须与加密时一致）
        
        Returns:
            解密后的图片 tensor
        """
        # 转换为 numpy 数组
        img_np = encrypted_image.cpu().numpy()
        batch_size, height, width, channels = img_np.shape
        
        # 使用密码生成随机种子
        seed = self._password_to_seed(password