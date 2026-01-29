package com.aivle0102.bigproject.security;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.security.web.csrf.CsrfToken;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;

/**
 * CSRF ?좏겙??紐낆떆?곸쑝濡?濡쒕뱶?섏뿬 荑좏궎 ?앹꽦??媛뺤젣?섎뒗 ?꾪꽣
 * Spring Security 6?먯꽌??CSRF ?좏겙??deferred 諛⑹떇?쇰줈 ?숈옉?섎?濡?
 * 紐낆떆?곸쑝濡??좏겙??濡쒕뱶?댁빞 荑좏궎媛 ?앹꽦??
 */
@Component
public class CsrfCookieFilter extends OncePerRequestFilter {

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {

        CsrfToken csrfToken = (CsrfToken) request.getAttribute(CsrfToken.class.getName());
        if (csrfToken != null) {
            // ?좏겙??紐낆떆?곸쑝濡?濡쒕뱶?섏뿬 荑좏궎 ?앹꽦??媛뺤젣??
            csrfToken.getToken();
        }

        filterChain.doFilter(request, response);
    }
}
