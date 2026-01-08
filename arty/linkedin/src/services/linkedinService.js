import axios from 'axios';
import FormData from 'form-data';
import { createReadStream, statSync } from 'fs';
import { readFile } from 'fs/promises';
import mime from 'mime-types';
import logger from '../utils/logger.js';
import { queries } from '../utils/database.js';

class LinkedInService {
  constructor(accessToken, config) {
    this.accessToken = accessToken;
    this.config = config;
    this.baseURL = process.env.LINKEDIN_API_BASE_URL || 'https://api.linkedin.com/v2';
    this.apiVersion = process.env.LINKEDIN_API_VERSION || '202501';
    
    this.client = axios.create({
      baseURL: this.baseURL,
      headers: {
        'Authorization': `Bearer ${this.accessToken}`,
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0',
        'LinkedIn-Version': this.apiVersion
      },
      timeout: 30000
    });
    
    // Add request interceptor for logging
    this.client.interceptors.request.use(
      (config) => {
        logger.debug(`API Request: ${config.method.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        logger.error('API Request Error:', error);
        return Promise.reject(error);
      }
    );
    
    // Add response interceptor for logging and rate limiting
    this.client.interceptors.response.use(
      (response) => {
        logger.api(response.config.method, response.config.url, response.status, response.config.metadata?.duration || 0);
        queries.recordApiCall(response.config.url);
        return response;
      },
      (error) => {
        if (error.response) {
          logger.error(`API Error: ${error.response.status} - ${JSON.stringify(error.response.data)}`);
        } else {
          logger.error('API Error:', error.message);
        }
        return Promise.reject(error);
      }
    );
  }
  
  /**
   * Create a text post on LinkedIn
   */
  async createTextPost(content, authorUrn, visibility = 'PUBLIC') {
    try {
      const postData = {
        author: authorUrn,
        lifecycleState: 'PUBLISHED',
        specificContent: {
          'com.linkedin.ugc.ShareContent': {
            shareCommentary: {
              text: content
            },
            shareMediaCategory: 'NONE'
          }
        },
        visibility: {
          'com.linkedin.ugc.MemberNetworkVisibility': visibility
        }
      };
      
      const response = await this.client.post('/ugcPosts', postData);
      const postId = response.data.id;
      
      logger.post('CREATE_TEXT', postId, { content: content.substring(0, 100), visibility });
      
      return {
        success: true,
        postId,
        data: response.data
      };
    } catch (error) {
      logger.error('Failed to create text post:', error);
      throw error;
    }
  }
  
  /**
   * Upload media to LinkedIn
   */
  async uploadMedia(filePath, authorUrn) {
    try {
      const stats = statSync(filePath);
      const mimeType = mime.lookup(filePath) || 'application/octet-stream';
      const mediaCategory = this.getMediaCategory(mimeType);
      
      // Step 1: Register upload
      const registerData = {
        registerUploadRequest: {
          recipes: [`urn:li:digitalmediaRecipe:feedshare-${mediaCategory}`],
          owner: authorUrn,
          serviceRelationships: [{
            relationshipType: 'OWNER',
            identifier: 'urn:li:userGeneratedContent'
          }]
        }
      };
      
      const registerResponse = await this.client.post('/assets?action=registerUpload', registerData);
      const uploadUrl = registerResponse.data.value.uploadMechanism['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest'].uploadUrl;
      const asset = registerResponse.data.value.asset;
      
      logger.info(`Media upload registered: ${asset}`);
      
      // Step 2: Upload file
      const fileBuffer = await readFile(filePath);
      await axios.put(uploadUrl, fileBuffer, {
        headers: {
          'Content-Type': mimeType
        }
      });
      
      logger.info(`Media uploaded successfully: ${filePath}`);
      
      return {
        success: true,
        asset,
        uploadUrl
      };
    } catch (error) {
      logger.error('Failed to upload media:', error);
      throw error;
    }
  }
  
  /**
   * Create a post with media (image/video/document)
   */
  async createMediaPost(content, authorUrn, mediaAssets, visibility = 'PUBLIC') {
    try {
      const media = mediaAssets.map(asset => ({
        status: 'READY',
        description: {
          text: ''
        },
        media: asset,
        title: {
          text: ''
        }
      }));
      
      const postData = {
        author: authorUrn,
        lifecycleState: 'PUBLISHED',
        specificContent: {
          'com.linkedin.ugc.ShareContent': {
            shareCommentary: {
              text: content
            },
            shareMediaCategory: 'IMAGE',
            media
          }
        },
        visibility: {
          'com.linkedin.ugc.MemberNetworkVisibility': visibility
        }
      };
      
      const response = await this.client.post('/ugcPosts', postData);
      const postId = response.data.id;
      
      logger.post('CREATE_MEDIA', postId, { content: content.substring(0, 100), mediaCount: mediaAssets.length });
      
      return {
        success: true,
        postId,
        data: response.data
      };
    } catch (error) {
      logger.error('Failed to create media post:', error);
      throw error;
    }
  }
  
  /**
   * Get post analytics/statistics
   */
  async getPostAnalytics(postUrn) {
    try {
      const response = await this.client.get(`/socialActions/${encodeURIComponent(postUrn)}`);
      
      const analytics = {
        likes: response.data.likesSummary?.totalLikes || 0,
        comments: response.data.commentsSummary?.totalComments || 0,
        shares: response.data.sharesSummary?.totalShares || 0
      };
      
      logger.info(`Fetched analytics for post: ${postUrn}`);
      
      return {
        success: true,
        analytics
      };
    } catch (error) {
      logger.error('Failed to get post analytics:', error);
      throw error;
    }
  }
  
  /**
   * Delete a post
   */
  async deletePost(postUrn) {
    try {
      await this.client.delete(`/ugcPosts/${encodeURIComponent(postUrn)}`);
      
      logger.post('DELETE', postUrn, {});
      
      return {
        success: true,
        message: 'Post deleted successfully'
      };
    } catch (error) {
      logger.error('Failed to delete post:', error);
      throw error;
    }
  }
  
  /**
   * Get user profile information
   */
  async getUserProfile() {
    try {
      const response = await this.client.get('/me');
      
      logger.info('Fetched user profile');
      
      return {
        success: true,
        profile: response.data
      };
    } catch (error) {
      logger.error('Failed to get user profile:', error);
      throw error;
    }
  }
  
  /**
   * Get organization/company page information
   */
  async getOrganization(organizationId) {
    try {
      const response = await this.client.get(`/organizations/${organizationId}`);
      
      logger.info(`Fetched organization: ${organizationId}`);
      
      return {
        success: true,
        organization: response.data
      };
    } catch (error) {
      logger.error('Failed to get organization:', error);
      throw error;
    }
  }
  
  /**
   * Helper: Determine media category from MIME type
   */
  getMediaCategory(mimeType) {
    if (mimeType.startsWith('image/')) return 'image';
    if (mimeType.startsWith('video/')) return 'video';
    if (mimeType.includes('pdf') || mimeType.includes('document')) return 'document';
    return 'image';
  }
  
  /**
   * Check API rate limits
   */
  checkRateLimit(endpoint) {
    const hourlyLimit = this.config.rateLimiting?.limits?.postsPerHour || 25;
    const dailyLimit = this.config.rateLimiting?.limits?.postsPerDay || 100;
    
    const hourlyOk = queries.checkRateLimit(endpoint, hourlyLimit, 3600000);
    const dailyOk = queries.checkRateLimit(endpoint, dailyLimit, 86400000);
    
    return hourlyOk && dailyOk;
  }
}

export default LinkedInService;
