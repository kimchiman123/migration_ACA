package com.aivle0102.bigproject.security;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.authentication.WebAuthenticationDetailsSource;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.Collections;
import java.util.List;

@Slf4j
@Component
@RequiredArgsConstructor
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    private final JwtTokenProvider jwtTokenProvider;

    // 인증이 필요 없는 경로는 JWT 필터를 건너뜀
    @Override
    protected boolean shouldNotFilter(HttpServletRequest request) {
        String path = request.getRequestURI();
        return path.startsWith("/api/auth/") ||
                path.equals("/api/health") ||
                path.startsWith("/oauth2/") ||
                path.startsWith("/login/oauth2/") ||
                path.equals("/error");
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {

        String requestUri = request.getRequestURI();
        String authHeader = request.getHeader("Authorization");

        // 디버그 로그: Authorization 헤더 수신 여부
        log.debug("[JWT Filter] URI: {}, Authorization Header Present: {}", requestUri, authHeader != null);

        if (authHeader != null) {
            log.debug("[JWT Filter] Authorization Header Value: {}",
                    authHeader.length() > 20 ? authHeader.substring(0, 20) + "..." : authHeader);
        }

        String token = resolveToken(request);

        if (token != null) {
            log.debug("[JWT Filter] Token extracted successfully, length: {}", token.length());

            try {
                if (jwtTokenProvider.validateToken(token)) {
                    String userId = jwtTokenProvider.getUserId(token);
                    String role = jwtTokenProvider.getRole(token);

                    log.info("[JWT Filter] Token validated successfully for user: {}, role: {}", userId, role);

                    // 권한(Role) 설정 - 기본값은 ROLE_USER
                    List<SimpleGrantedAuthority> authorities;
                    if (role != null && !role.isEmpty()) {
                        authorities = List.of(new SimpleGrantedAuthority(role));
                    } else {
                        authorities = List.of(new SimpleGrantedAuthority("ROLE_USER"));
                    }

                    log.debug("[JWT Filter] Granted Authorities: {}", authorities);

                    UsernamePasswordAuthenticationToken authentication = new UsernamePasswordAuthenticationToken(
                            userId,
                            null,
                            authorities);

                    authentication.setDetails(new WebAuthenticationDetailsSource().buildDetails(request));
                    SecurityContextHolder.getContext().setAuthentication(authentication);
                } else {
                    log.warn("[JWT Filter] Token validation failed for URI: {}", requestUri);
                }
            } catch (Exception e) {
                log.error("[JWT Filter] Token parsing/validation error: {}", e.getMessage());
            }
        } else {
            log.debug("[JWT Filter] No token found in request for URI: {}", requestUri);
        }

        filterChain.doFilter(request, response);
    }

    private String resolveToken(HttpServletRequest request) {
        String bearerToken = request.getHeader("Authorization");
        if (StringUtils.hasText(bearerToken) && bearerToken.startsWith("Bearer ")) {
            return bearerToken.substring(7);
        }
        return null;
    }
}
