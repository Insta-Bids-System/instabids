#!/usr/bin/env node

/**
 * Simple Docker MCP Server for InstaBids
 * Provides direct Docker container management tools
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { CallToolRequestSchema, ListToolsRequestSchema } from '@modelcontextprotocol/sdk/types.js';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

class DockerMCPServer {
  constructor() {
    this.server = new Server(
      {
        name: 'docker-mcp',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupToolHandlers();
  }

  setupToolHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          {
            name: 'docker_ps',
            description: 'List running Docker containers',
            inputSchema: {
              type: 'object',
              properties: {
                all: {
                  type: 'boolean',
                  description: 'Show all containers (default: false - only running)',
                  default: false
                }
              }
            }
          },
          {
            name: 'docker_logs',
            description: 'Get logs from a Docker container',
            inputSchema: {
              type: 'object',
              properties: {
                container: {
                  type: 'string',
                  description: 'Container name or ID'
                },
                tail: {
                  type: 'number',
                  description: 'Number of lines to show from end (default: 50)',
                  default: 50
                },
                follow: {
                  type: 'boolean',
                  description: 'Follow log output (default: false)',
                  default: false
                }
              },
              required: ['container']
            }
          },
          {
            name: 'docker_exec',
            description: 'Execute command inside Docker container',
            inputSchema: {
              type: 'object',
              properties: {
                container: {
                  type: 'string',
                  description: 'Container name or ID'
                },
                command: {
                  type: 'string',
                  description: 'Command to execute'
                }
              },
              required: ['container', 'command']
            }
          },
          {
            name: 'docker_compose_ps',
            description: 'List Docker Compose services status',
            inputSchema: {
              type: 'object',
              properties: {
                project_dir: {
                  type: 'string',
                  description: 'Path to docker-compose.yml directory',
                  default: 'C:\\Users\\Not John Or Justin\\Documents\\instabids'
                }
              }
            }
          },
          {
            name: 'docker_compose_logs',
            description: 'Get logs from Docker Compose services',
            inputSchema: {
              type: 'object',
              properties: {
                service: {
                  type: 'string',
                  description: 'Service name (optional - if not provided, shows all services)'
                },
                project_dir: {
                  type: 'string',
                  description: 'Path to docker-compose.yml directory',
                  default: 'C:\\Users\\Not John Or Justin\\Documents\\instabids'
                },
                tail: {
                  type: 'number',
                  description: 'Number of lines to show (default: 50)',
                  default: 50
                }
              }
            }
          },
          {
            name: 'docker_inspect',
            description: 'Get detailed information about a container',
            inputSchema: {
              type: 'object',
              properties: {
                container: {
                  type: 'string',
                  description: 'Container name or ID'
                }
              },
              required: ['container']
            }
          }
        ]
      };
    });

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case 'docker_ps':
            return await this.dockerPs(args);
          case 'docker_logs':
            return await this.dockerLogs(args);
          case 'docker_exec':
            return await this.dockerExec(args);
          case 'docker_compose_ps':
            return await this.dockerComposePs(args);
          case 'docker_compose_logs':
            return await this.dockerComposeLogs(args);
          case 'docker_inspect':
            return await this.dockerInspect(args);
          default:
            throw new Error(`Unknown tool: ${name}`);
        }
      } catch (error) {
        return {
          content: [
            {
              type: 'text',
              text: `Error executing ${name}: ${error.message}`
            }
          ]
        };
      }
    });
  }

  async dockerPs(args) {
    const allFlag = args.all ? '-a' : '';
    const { stdout, stderr } = await execAsync(`docker ps ${allFlag} --format "table {{.Names}}\\t{{.Image}}\\t{{.Status}}\\t{{.Ports}}"`);
    
    return {
      content: [
        {
          type: 'text',
          text: stdout || stderr
        }
      ]
    };
  }

  async dockerLogs(args) {
    const tailFlag = args.tail ? `--tail ${args.tail}` : '--tail 50';
    const followFlag = args.follow ? '-f' : '';
    const { stdout, stderr } = await execAsync(`docker logs ${tailFlag} ${followFlag} ${args.container}`);
    
    return {
      content: [
        {
          type: 'text',
          text: stdout || stderr
        }
      ]
    };
  }

  async dockerExec(args) {
    const { stdout, stderr } = await execAsync(`docker exec ${args.container} ${args.command}`);
    
    return {
      content: [
        {
          type: 'text',
          text: stdout || stderr
        }
      ]
    };
  }

  async dockerComposePs(args) {
    const projectDir = args.project_dir || 'C:\\Users\\Not John Or Justin\\Documents\\instabids';
    const { stdout, stderr } = await execAsync(`docker-compose ps`, { cwd: projectDir });
    
    return {
      content: [
        {
          type: 'text',
          text: stdout || stderr
        }
      ]
    };
  }

  async dockerComposeLogs(args) {
    const projectDir = args.project_dir || 'C:\\Users\\Not John Or Justin\\Documents\\instabids';
    const serviceFlag = args.service ? args.service : '';
    const tailFlag = args.tail ? `--tail=${args.tail}` : '--tail=50';
    const { stdout, stderr } = await execAsync(`docker-compose logs ${tailFlag} ${serviceFlag}`, { cwd: projectDir });
    
    return {
      content: [
        {
          type: 'text',
          text: stdout || stderr
        }
      ]
    };
  }

  async dockerInspect(args) {
    const { stdout, stderr } = await execAsync(`docker inspect ${args.container}`);
    
    return {
      content: [
        {
          type: 'text',
          text: stdout || stderr
        }
      ]
    };
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('Docker MCP Server running on stdio');
  }
}

const server = new DockerMCPServer();
server.run().catch(console.error);